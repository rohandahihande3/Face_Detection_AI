# OpenCV_demo

📦 **OpenCV Face Detection App (React + Flask + Docker)**

This project is a complete **Fullstack Face Detection System** built with:

- **Frontend:** React + Nginx  
- **Backend:** Flask + OpenCV  
- **Containerization:** Docker & Docker Compose  

The app allows users to upload images or use their camera for real-time face detection, powered by OpenCV Haar Cascades.

---

## 🚀 Features

### 🖥️ Frontend (React + Nginx)
- Compact single-page UI for image upload, camera capture, live detection, and AI chat
- Camera frames are downscaled before upload to reduce CPU and memory pressure
- Production Nginx serves static files and proxies `/api/*` to Flask, so one EC2 public port is enough

### ⚙️ Backend (Flask + OpenCV)
- REST API for image detection  
- Real-time detection endpoint for live camera stream  
- Uses Haar Cascade `.xml` models for:
  - Face  
  - Eyes  
  - Nose  
  - Mouth  

### 🐳 Dockerized Setup
- Multi-stage frontend Docker build (Node → Nginx)  
- Python backend with OpenCV dependencies  
- Easy orchestration using Docker Compose  

---

## 📂 Project Structure
```bash
OpenCV_demo/
│
├── backend/
│ ├── app/
│ │ ├── API/
│ │ │ ├── cv.py
│ │ │ ├── consumer.py
│ │ ├── main.py
│ │ ├── xml_files/
│ ├── run.py
│ ├── requirements.txt
│ ├── Dockerfile
│
│
├── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│ ├── nginx.conf
│ └── Dockerfile
│
├── docker-compose.yml
└── README.md


---
```
## 🛠️ How to Run Locally (Without Docker)

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python run.py

```
### 2.Frontend
```bash
cd frontend
npm install
npm start

```
### 🐳 Running with Docker Compose (Recommended)
```bash
From the project root:
Build & Start

docker compose up --build

```
The frontend is available at:
```bash
http://YOUR_EC2_PUBLIC_IP
```

The backend stays inside the Docker network. Nginx forwards `/api/*` to Flask, so your EC2 security group only needs inbound HTTP on port `80`.

Camera access requires a secure browser origin. Image upload works on `http://YOUR_EC2_PUBLIC_IP`, but webcam mode needs either `http://localhost` during development or `https://your-domain.com` in production.

If you run the React dev server instead of Docker, point it to Flask:
```bash
REACT_APP_API_BASE_URL=http://localhost:5000 npm start
```

### Start Without Rebuilding
```bash
docker compose up

``` 
### Stop Containers
```bash
docker compose down
