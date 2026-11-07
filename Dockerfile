# Multi-stage build: React Vite frontend + FastAPI Python backend
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.12-slim
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./backend/
COPY models/ ./models/
COPY controllers/ ./controllers/
COPY uploads/ ./uploads/
COPY saved_indexes/ ./saved_indexes/

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PORT=8000
EXPOSE 8000

# Start Uvicorn bound to 0.0.0.0 and dynamic $PORT provided by Render
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
