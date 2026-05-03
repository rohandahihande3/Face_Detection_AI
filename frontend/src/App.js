import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  Camera,
  CircleStop,
  FileText,
  ImageUp,
  Loader2,
  RefreshCw,
  Send,
  Upload,
  Video,
  X,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_BASE = (process.env.REACT_APP_API_BASE_URL || "/api").replace(/\/$/, "");
const MAX_FRAME_WIDTH = 640;
const LIVE_FRAME_DELAY = 1200;
const CAMERA_SECURITY_MESSAGE =
  "Camera access needs HTTPS or localhost. You are opening the app from a plain IP address, so upload an image or serve the site with HTTPS.";

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

function App() {
  const [activeTool, setActiveTool] = useState("detect");
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedPreview, setSelectedPreview] = useState("");
  const [processedImage, setProcessedImage] = useState("");
  const [detectError, setDetectError] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [liveRunning, setLiveRunning] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Upload PDFs for document questions, or ask a general question.",
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [documents, setDocuments] = useState([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [uploadingDocs, setUploadingDocs] = useState(false);
  const [chatError, setChatError] = useState("");

  const imageInputRef = useRef(null);
  const docInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const liveTimerRef = useRef(null);
  const inFlightLiveRef = useRef(false);
  const messagesEndRef = useRef(null);

  const statusText = useMemo(() => {
    if (isProcessing) return "Processing image";
    if (liveRunning) return "Live detection active";
    if (cameraReady) return "Camera ready";
    return "Ready";
  }, [cameraReady, isProcessing, liveRunning]);

  const clearObjectUrl = useCallback((url) => {
    if (url) URL.revokeObjectURL(url);
  }, []);

  const resetImage = useCallback(() => {
    setSelectedImage(null);
    setSelectedPreview((current) => {
      clearObjectUrl(current);
      return "";
    });
    setProcessedImage((current) => {
      clearObjectUrl(current);
      return "";
    });
    setDetectError("");
    if (imageInputRef.current) imageInputRef.current.value = "";
  }, [clearObjectUrl]);

  const stopLiveDetection = useCallback(() => {
    if (liveTimerRef.current) {
      clearInterval(liveTimerRef.current);
      liveTimerRef.current = null;
    }
    inFlightLiveRef.current = false;
    setLiveRunning(false);
  }, []);

  const stopCamera = useCallback(() => {
    stopLiveDetection();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraActive(false);
    setCameraReady(false);
  }, [stopLiveDetection]);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, chatBusy]);

  const drawVideoToBlob = useCallback(
    (quality = 0.76) =>
      new Promise((resolve, reject) => {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        if (!video || !canvas || video.videoWidth === 0) {
          reject(new Error("Camera frame is not ready yet."));
          return;
        }

        const scale = Math.min(1, MAX_FRAME_WIDTH / video.videoWidth);
        canvas.width = Math.round(video.videoWidth * scale);
        canvas.height = Math.round(video.videoHeight * scale);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(
          (blob) => (blob ? resolve(blob) : reject(new Error("Unable to capture frame."))),
          "image/jpeg",
          quality
        );
      }),
    []
  );

  const processImage = useCallback(
    async (fileOrBlob) => {
      setIsProcessing(true);
      setDetectError("");
      const formData = new FormData();
      formData.append("image", fileOrBlob, fileOrBlob.name || "capture.jpg");

      try {
        const response = await fetch(apiUrl("/detect"), {
          method: "POST",
          body: formData,
        });
        if (!response.ok) throw new Error(`Server returned ${response.status}`);

        const blob = await response.blob();
        const nextUrl = URL.createObjectURL(blob);
        setProcessedImage((current) => {
          clearObjectUrl(current);
          return nextUrl;
        });
      } catch (error) {
        setDetectError(error.message);
      } finally {
        setIsProcessing(false);
      }
    },
    [clearObjectUrl]
  );

  const handleImageSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setDetectError("Choose a JPG, PNG, or WEBP image.");
      return;
    }

    resetImage();
    setSelectedImage(file);
    setSelectedPreview(URL.createObjectURL(file));
    await processImage(file);
  };

  const startCamera = async () => {
    try {
      setDetectError("");
      stopCamera();

      if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
        setDetectError(CAMERA_SECURITY_MESSAGE);
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 960 },
          height: { ideal: 540 },
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;
      setCameraActive(true);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setCameraReady(true);
      }
    } catch (error) {
      setDetectError(`Camera unavailable: ${error.message}`);
      stopCamera();
    }
  };

  const capturePhoto = async () => {
    try {
      const blob = await drawVideoToBlob(0.86);
      stopCamera();
      resetImage();
      const previewUrl = URL.createObjectURL(blob);
      setSelectedImage(new File([blob], "camera-capture.jpg", { type: "image/jpeg" }));
      setSelectedPreview(previewUrl);
      await processImage(blob);
    } catch (error) {
      setDetectError(error.message);
    }
  };

  const processLiveFrame = useCallback(async () => {
    if (inFlightLiveRef.current || !cameraReady) return;
    inFlightLiveRef.current = true;

    try {
      const blob = await drawVideoToBlob(0.64);
      const formData = new FormData();
      formData.append("image", blob, "live-frame.jpg");
      const response = await fetch(apiUrl("/detect-live"), {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error(`Server returned ${response.status}`);

      const imageBlob = await response.blob();
      const nextUrl = URL.createObjectURL(imageBlob);
      setProcessedImage((current) => {
        clearObjectUrl(current);
        return nextUrl;
      });
    } catch (error) {
      setDetectError(error.message);
      stopLiveDetection();
    } finally {
      inFlightLiveRef.current = false;
    }
  }, [cameraReady, clearObjectUrl, drawVideoToBlob, stopLiveDetection]);

  const startLiveDetection = () => {
    if (!cameraReady) {
      setDetectError("Start the camera before live detection.");
      return;
    }
    setDetectError("");
    setLiveRunning(true);
    processLiveFrame();
    liveTimerRef.current = setInterval(processLiveFrame, LIVE_FRAME_DELAY);
  };

  const uploadDocuments = async (event) => {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    setUploadingDocs(true);
    setChatError("");
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch(apiUrl("/upload"), {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error(`Upload failed with ${response.status}`);

      const data = await response.json();
      const nextDocs = files.map((file, index) => ({
        name: file.name,
        id: data.file_ids?.[index] || file.name,
      }));
      setDocuments((current) => [...current, ...nextDocs]);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: `${files.length} document${files.length > 1 ? "s" : ""} uploaded. Ask a question about them.`,
        },
      ]);
    } catch (error) {
      setChatError(error.message);
    } finally {
      setUploadingDocs(false);
      if (docInputRef.current) docInputRef.current.value = "";
    }
  };

  const sendMessage = async () => {
    const question = chatInput.trim();
    if (!question || chatBusy) return;

    setChatInput("");
    setChatBusy(true);
    setChatError("");
    setMessages((current) => [...current, { role: "user", text: question }]);

    const hasDocs = documents.length > 0;
    try {
      const response = await fetch(apiUrl(hasDocs ? "/ask" : "/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          hasDocs
            ? { question, document_ids: documents.map((doc) => doc.id) }
            : { message: question }
        ),
      });
      if (!response.ok) throw new Error(`Server returned ${response.status}`);

      const data = await response.json();
      setMessages((current) => [
        ...current,
        { role: "assistant", text: data.answer || data.response || data.msg || "No response returned." },
      ]);
    } catch (error) {
      setChatError(error.message);
      setMessages((current) => [
        ...current,
        { role: "assistant", text: "I could not reach the backend. Check Flask, Nginx, and the API key." },
      ]);
    } finally {
      setChatBusy(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">OpenCV + AI assistant</p>
          <h1>Face Detection AI</h1>
        </div>
        <div className="status-pill">{statusText}</div>
      </section>

      <nav className="tool-tabs" aria-label="Tool selector">
        <button
          className={activeTool === "detect" ? "active" : ""}
          onClick={() => setActiveTool("detect")}
        >
          <Camera size={18} />
          Detection
        </button>
        <button className={activeTool === "chat" ? "active" : ""} onClick={() => setActiveTool("chat")}>
          <Bot size={18} />
          Assistant
        </button>
      </nav>

      {activeTool === "detect" ? (
        <section className="workspace detect-grid">
          <div className="panel controls-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Input</p>
                <h2>Upload or camera</h2>
              </div>
              {(selectedImage || cameraActive) && (
                <button className="icon-button" onClick={() => { stopCamera(); resetImage(); }} title="Reset">
                  <RefreshCw size={18} />
                </button>
              )}
            </div>

            <input
              ref={imageInputRef}
              className="hidden-input"
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
            />
            <button className="upload-zone" onClick={() => imageInputRef.current?.click()}>
              <ImageUp size={34} />
              <span>Choose image</span>
            </button>

            <div className="camera-box">
              <video ref={videoRef} muted playsInline className={cameraActive ? "" : "empty-video"} />
              {!cameraActive && (
                <button className="primary-button" onClick={startCamera}>
                  <Video size={18} />
                  Start camera
                </button>
              )}
            </div>

            {cameraActive && (
              <div className="button-row">
                <button className="primary-button" onClick={capturePhoto} disabled={!cameraReady}>
                  <Camera size={18} />
                  Capture
                </button>
                <button
                  className="secondary-button"
                  onClick={liveRunning ? stopLiveDetection : startLiveDetection}
                  disabled={!cameraReady}
                >
                  {liveRunning ? <CircleStop size={18} /> : <Video size={18} />}
                  {liveRunning ? "Stop live" : "Live"}
                </button>
                <button className="ghost-button" onClick={stopCamera}>
                  <X size={18} />
                  Stop
                </button>
              </div>
            )}

            {detectError && <p className="error-text">{detectError}</p>}
          </div>

          <div className="panel result-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Output</p>
                <h2>Detection result</h2>
              </div>
              {isProcessing && <Loader2 className="spin" size={20} />}
            </div>
            <div className="preview-grid">
              <div className="preview-slot">
                <span>Original</span>
                {selectedPreview ? <img src={selectedPreview} alt="Original upload" /> : <div>No image yet</div>}
              </div>
              <div className="preview-slot">
                <span>Processed</span>
                {processedImage ? <img src={processedImage} alt="Processed detection" /> : <div>No result yet</div>}
              </div>
            </div>
          </div>
          <canvas ref={canvasRef} className="hidden-input" />
        </section>
      ) : (
        <section className="workspace chat-layout">
          <aside className="panel docs-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Documents</p>
                <h2>PDF context</h2>
              </div>
            </div>
            <input
              ref={docInputRef}
              className="hidden-input"
              type="file"
              multiple
              accept=".pdf"
              onChange={uploadDocuments}
            />
            <button className="primary-button full-width" onClick={() => docInputRef.current?.click()} disabled={uploadingDocs}>
              {uploadingDocs ? <Loader2 className="spin" size={18} /> : <Upload size={18} />}
              {uploadingDocs ? "Uploading" : "Upload PDFs"}
            </button>
            <div className="doc-list">
              {documents.length ? (
                documents.map((doc) => (
                  <div className="doc-row" key={doc.id}>
                    <FileText size={18} />
                    <span>{doc.name}</span>
                    <button
                      className="icon-button"
                      onClick={() => setDocuments((current) => current.filter((item) => item.id !== doc.id))}
                      title="Remove document"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))
              ) : (
                <p className="muted">No PDFs uploaded.</p>
              )}
            </div>
            {chatError && <p className="error-text">{chatError}</p>}
          </aside>

          <div className="panel chat-panel">
            <div className="messages">
              {messages.map((message, index) => (
                <div
                  className={`message ${message.role}${message.role === "assistant" ? " markdown-message" : ""}`}
                  key={`${message.role}-${index}`}
                >
                  {message.role === "assistant" ? (
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  ) : (
                    message.text
                  )}
                </div>
              ))}
              {chatBusy && (
                <div className="message assistant loading">
                  <Loader2 className="spin" size={17} />
                  Thinking
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="composer">
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") sendMessage();
                }}
                placeholder={documents.length ? "Ask about your uploaded PDFs" : "Ask a general question"}
                disabled={chatBusy}
              />
              <button className="primary-button send-button" onClick={sendMessage} disabled={chatBusy || !chatInput.trim()}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
