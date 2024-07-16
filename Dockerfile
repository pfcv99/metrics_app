# metrics_app/Dockerfile

FROM ubuntu:24.04

WORKDIR /metrics_app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/pfcv99/metrics_app.git -b optimization .

# Change to the cloned repository directory
WORKDIR /metrics_app

# Install conda dependencies
RUN conda install -y --file conda_requirements.txt \
    && conda clean -a -y

# Install pip dependencies
RUN pip install -r pip_requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
