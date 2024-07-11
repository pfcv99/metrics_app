# metrics_app/Dockerfile

FROM ubuntu:22.04

WORKDIR /metrics_app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    pip \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/pfcv99/metrics_app.git -b optimization .

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app\Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
