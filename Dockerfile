FROM python:3.11-slim

WORKDIR /app

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env .

# Ensure storage directories exist
RUN mkdir -p workspace outputs

EXPOSE 7860

# Run the Gradio intelligence console by default
CMD ["python", "frontend/app.py"]
