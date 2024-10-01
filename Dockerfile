FROM python:3.12.1-slim

WORKDIR /metrics_app  # Set working directory to /metrics_app

# Install essential dependencies and development tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libncurses5-dev \
    libncursesw5-dev \
    autoconf \
    automake \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository into the current directory (no nested /metrics_app directory)
RUN git clone --branch pfcv99-stable-version https://github.com/pfcv99/metrics_app.git .

# Install Python dependencies from requirements.txt
RUN pip install --upgrade pip==23.3.1
RUN pip install -r requirements.txt

# Download and install htslib
RUN curl -L https://github.com/samtools/htslib/releases/download/1.19/htslib-1.19.tar.bz2 | tar -xj && \
    cd htslib-1.19 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd ..

# Download and install Samtools
RUN curl -L https://github.com/samtools/samtools/releases/download/1.19/samtools-1.19.tar.bz2 | tar -xj && \
    cd samtools-1.19 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd ..

# Expose the Streamlit port
EXPOSE 8501

# Healthcheck for Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the entry point for Streamlit, pointing to the Home.py inside the app folder
ENTRYPOINT ["streamlit", "run", "/metrics_app/app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
