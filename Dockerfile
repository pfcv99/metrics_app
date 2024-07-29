FROM ubuntu:24.04

WORKDIR /metrics_app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    python3-wheel && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3.12 -m venv /home/myuser/venv --system-site-packages

# Set environment variables
ENV VIRTUAL_ENV=/home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Clone the repository (or consider using COPY if you have the repo locally)
RUN git clone -b optimization https://github.com/pfcv99/metrics_app.git .

# Install Python packages
RUN pip install --no-cache-dir wheel streamlit

# Expose the port the app runs on
EXPOSE 8501

# Healthcheck to verify if the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the entry point for the container
ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=172.19.16.1"]
