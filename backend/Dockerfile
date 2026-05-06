# FROM python:3.10-slim

# # Install system libs needed by OpenCV
# RUN apt-get update && apt-get install -y \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend code
# COPY . .

# EXPOSE 5000

# CMD ["python", "run.py"]


FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --upgrade pip

# ✅ GPU torch
# Torch (FIXED VERSION)
RUN pip install --no-cache-dir \
    torch==2.3.1 \
    torchvision==0.18.1 \
    torchaudio==2.3.1 \
    --index-url https://download.pytorch.org/whl/cu121

# OpenCV + numpy
RUN pip install --no-cache-dir numpy==2.2.6 opencv-python-headless==4.10.0.84

# YOLO
RUN pip install --no-cache-dir ultralytics==8.2.0 

# Required missing dep
RUN pip install --no-cache-dir psutil

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
