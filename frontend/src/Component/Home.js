import React, { useState, useRef, useEffect } from "react";
import { Camera, Upload, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
const BACKEND_URL = process.env.BACKEND_URL
export default function Home() {
    const [mode, setMode] = useState("upload");
    const navigate = useNavigate();

    const [selectedImage, setSelectedImage] = useState(null);
    const [processedImage, setProcessedImage] = useState(null);

    const [cameraStream, setCameraStream] = useState(null);
    const [cameraReady, setCameraReady] = useState(false);

    const [liveProcessed, setLiveProcessed] = useState(null);
    const liveIntervalRef = useRef(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);

    // ---------------------------
    // START CAMERA
    // ---------------------------
    const startCamera = async () => {
        try {
            setError("");
            setCameraReady(false);

            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: false,
            });

            setCameraStream(stream);

            setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    videoRef.current.onloadedmetadata = () => {
                        videoRef.current.play();
                        setCameraReady(true);
                    };
                }
            }, 200);
        } catch (err) {
            setError("Camera error: " + err.message);
        }
    };

    // ---------------------------
    // STOP CAMERA + STOP LIVE LOOP
    // ---------------------------
    const stopCamera = () => {
        if (cameraStream) {
            cameraStream.getTracks().forEach((t) => t.stop());
        }
        setCameraStream(null);
        setCameraReady(false);

        if (liveIntervalRef.current) {
            clearInterval(liveIntervalRef.current);
            liveIntervalRef.current = null;
        }

        setLiveProcessed(null);

        if (videoRef.current) videoRef.current.srcObject = null;
    };

    const captureAndProcess = () => {
        const video = videoRef.current;
        const canvas = canvasRef.current;

        if (!canvas || !video) {
            setError("Camera not ready.");
            return;
        }

        // Set canvas to video size
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(async (blob) => {
            if (!blob) {
                setError("Failed to capture image.");
                return;
            }

            // Convert blob to file
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" });

            // Update UI state
            setSelectedImage(file);
            setMode("upload"); // switch to upload mode UI
            stopCamera();

            // Now send to backend
            setLoading(true);
            const formData = new FormData();
            formData.append("image", file);

            try {
                const response = await fetch(`${BACKEND_URL}/detect`, {
                    method: "POST",
                    body: formData,
                });

                const processedBlob = await response.blob();
                setProcessedImage(URL.createObjectURL(processedBlob));
            } catch (err) {
                setError("Processing error: " + err.message);
            }

            setLoading(false);
        }, "image/jpeg");
    };



    // ---------------------------
    // FILE UPLOAD HANDLER
    // ---------------------------
    const handleFileSelect = async (e) => {
        const file = e.target.files[0];

        if (!file || !file.type.startsWith("image/")) {
            setError("Please select a valid image file.");
            return;
        }

        // Set selected image so UI shows original
        setSelectedImage(file);
        setProcessedImage(null);
        setError("");

        // Auto-hit detect API
        setLoading(true);

        const formData = new FormData();
        formData.append("image", file);

        try {
            const response = await fetch(`${BACKEND_URL}/detect`, {
                method: "POST",
                body: formData,
            });

            const blob = await response.blob();
            setProcessedImage(URL.createObjectURL(blob));
        } catch (err) {
            setError("Processing error: " + err.message);
        }

        setLoading(false);
    };

    // ---------------------------
    // PROCESS IMAGE (UPLOAD MODE)
    // ---------------------------
    const processImage = async () => {
        if (!selectedImage) return;

        setLoading(true);

        const formData = new FormData();
        formData.append("image", selectedImage);

        try {
            const response = await fetch(`${BACKEND_URL}/detect`, {
                method: "POST",
                body: formData,
            });

            const blob = await response.blob();
            setProcessedImage(URL.createObjectURL(blob));
        } catch (err) {
            setError("Processing error: " + err.message);
        }

        setLoading(false);
    };

    const startLiveDetection = () => {
        if (!cameraReady || !videoRef.current || !canvasRef.current) {
            console.warn("Camera not ready for live detection.");
            return;
        }
    
        // Run at a safe 300ms instead of 100ms (prevents backend overload)
        liveIntervalRef.current = setInterval(async () => {
            const video = videoRef.current;
            const canvas = canvasRef.current;
    
            if (!video || !canvas) return;
    
            // Video may not be fully ready at first
            if (video.videoWidth === 0 || video.videoHeight === 0) {
                console.warn("Skipping frame — video not ready.");
                return;
            }
    
            // Set canvas size to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
    
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0);
    
            canvas.toBlob(async (blob) => {
                if (!blob) {
                    console.warn("Skipping frame — blob was null.");
                    return;
                }
    
                const formData = new FormData();
                formData.append("image", blob, "frame.jpg");
    
                try {
                    const res = await fetch(`${BACKEND_URL}/detect-live`, {
                        method: "POST",
                        body: formData,
                    });
    
                    const processedBlob = await res.blob();
                    setLiveProcessed(URL.createObjectURL(processedBlob));
                } catch (err) {
                    console.log("Live detection error:", err.message);
                }
            }, "image/jpeg");
        },400); // safer interval
    };
    

    // ---------------------------
    // MODE SWITCH
    // ---------------------------
    const switchMode = (m) => {
        setMode(m);
        stopCamera();
        setSelectedImage(null);
        setProcessedImage(null);
        setError("");
    };

    // ---------------------------
    // RESET UI
    // ---------------------------
    const reset = () => {
        stopCamera();
        setSelectedImage(null);
        setProcessedImage(null);
        setLiveProcessed(null);
    };

    useEffect(() => {
        return () => stopCamera();
    }, []);

    return (
        <div className="app">
            <div className="container">
                <h1 className="title">Face Detection App</h1>
                <p className="subtitle">Upload an image or use your camera to detect features</p>

                {/* Mode Buttons */}
                <div className="mode-buttons">
                    <button
                        className={`mode-btn ${mode === "upload" ? "active" : ""}`}
                        onClick={() => switchMode("upload")}
                    >
                        <Upload size={20} />
                        Upload Image
                    </button>

                    <button
                        className={`mode-btn ${mode === "camera" ? "active" : ""}`}
                        onClick={() => switchMode("camera")}
                    >
                        <Camera size={20} />
                        Use Camera
                    </button>

                    <button
                        className={`mode-btn ${mode === "camera" ? "active" : ""}`}
                        style={{ backgroundColor: "#800080", color: "white" }}
                        onClick={() => navigate("/Chat")}>
                        AI Document Assistance
                    </button>

                </div>

                {error && <div className="error-box">{error}</div>}

                {/* ---------------- UPLOAD MODE ---------------- */}
                {mode === "upload" && !selectedImage && (
                    <div className="card">
                        <div className="upload-area" onClick={() => fileInputRef.current.click()}>
                            <Upload className="upload-icon" size={48} />
                            <p>Click to upload an image</p>
                        </div>
                        <input type="file" ref={fileInputRef} className="file-input" onChange={handleFileSelect} />
                    </div>
                )}

                {/* ---------------- CAMERA MODE ---------------- */}
                {mode === "camera" && (
                    <div className="camera-layout">
                        {/* Left side: live video */}
                        <div className="camera-card">
                            <video
                                ref={videoRef}
                                autoPlay
                                muted
                                playsInline
                                className="camera-video"
                                style={{ display: cameraStream ? "block" : "none" }}
                            />

                            {!cameraStream && (
                                <button className="btn btn-primary big-btn" onClick={startCamera}>
                                    Start Camera
                                </button>
                            )}

                            {cameraStream && (
                                <div className="action-buttons">
                                    <button className="btn btn-primary" onClick={captureAndProcess}>
                                        Capture Photo
                                    </button>

                                    <button className="btn btn-primary" onClick={startLiveDetection}>
                                        Start Live Detection
                                    </button>

                                    <button className="btn btn-secondary" onClick={stopCamera}>
                                        Stop Camera
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Right side: live processed frame */}
                        {liveProcessed && (
                            <div className="processed-card">
                                <h2 className="processed-title">Processed Preview</h2>
                                <img src={liveProcessed} className="processed-img" alt="Processed" />
                            </div>
                        )}
                    </div>
                )}

                {/* ---------------- IMAGE RESULT (UPLOAD MODE) ---------------- */}
                {selectedImage && mode === "upload" && (
                    <div className="card">
                        <div className="result-header">
                            <h2>{processedImage ? "Detection Results" : "Selected Image"}</h2>
                            <button className="clear-btn" onClick={reset}>
                                <X size={20} /> Clear
                            </button>
                        </div>

                        <div className="image-grid">
                            <div>
                                <h3>Original</h3>
                                <img src={URL.createObjectURL(selectedImage)} alt="Original" />
                            </div>

                            <div>
                                <h3>Processed</h3>
                                {processedImage ? (
                                    <img src={processedImage} alt="Processed" />
                                ) : (
                                    <div className="placeholder">No results yet</div>
                                )}
                            </div>
                        </div>

                        {!processedImage && (
                            <div className="process-container">
                                <button className="btn btn-primary" onClick={processImage} disabled={loading}>
                                    {loading ? "Processing…" : "Detect Features"}
                                </button>
                            </div>
                        )}
                    </div>
                )}

                <canvas ref={canvasRef} className="hidden" />
            </div>
        </div>
    );
}