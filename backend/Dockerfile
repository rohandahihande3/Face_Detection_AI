# FROM python:3.10-slim

# # Install system libs needed by OpenCV
# RUN apt-get update && apt-get install -y \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Install Python dependencies
# COPY requirements.txt .
# RUN python -m pip install --upgrade pip && \
#     pip install --timeout 180 --retries 12 --progress-bar off -r requirements.txt || \
#     (sleep 8 && pip install --timeout 180 --retries 12 --progress-bar off -r requirements.txt)

# # Copy backend code
# COPY . .

# EXPOSE 5000

# CMD ["python", "run.py"]


FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --upgrade pip

# ✅ Step 1: install torch ONLY from pytorch index
# RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# ✅ Step 2: install other heavy deps from default PyPI
RUN pip install --no-cache-dir \
    numpy==2.2.6 \
    opencv-python-headless==4.10.0.84

RUN pip install --no-cache-dir psutil

# ✅ Step 3: ultralytics (no extra deps)
RUN pip install --no-cache-dir ultralytics==8.2.0 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OMP_NUM_THREADS=8
ENV MKL_NUM_THREADS=8

EXPOSE 5000

CMD ["python", "run.py"]