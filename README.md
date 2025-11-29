# OpenCV_demo

📦 **OpenCV Face Detection App (React + Flask + Docker)**

This project is a complete **Fullstack Face Detection System** built with:

- **Frontend:** React + Nginx  
- **Backend:** Flask + OpenCV  
- **Containerization:** Docker & Docker Compose  

The app allows users to upload images or use their camera for real-time face detection, powered by OpenCV Haar Cascades.

---

## 🚀 Features

### 🖥️ Frontend (React)
- Clean UI with image upload and webcam support  
- Live face detection with streamed frames  
- Fast production build served via Nginx  

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
### Start Without Rebuilding
```bash
docker compose up

``` 
### Stop Containers
```bash
docker compose down



