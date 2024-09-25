FROM ubuntu:23.10

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /metrics_app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    samtools \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3.12 -m venv /opt/venv

# Activate the virtual environment and upgrade pip
RUN /opt/venv/bin/pip install --upgrade pip

# Copy the requirements and install dependencies in the virtual environment
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Entry point
ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
