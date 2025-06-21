# Multi-stage Docker build for Ketto Care
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/yarn.lock* ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY ketto_care.db .

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./static

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]