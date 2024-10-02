# Usar a imagem base slim do Python
FROM python:3.12.1-slim

# Definir o diretório de trabalho
WORKDIR /metrics_app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libncurses5-dev \
    libncursesw5-dev \
    autoconf \
    automake \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg62-turbo-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Instalar Miniconda
RUN curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda clean --all && \
    ln -s /opt/conda/bin/conda /usr/local/bin/conda

# Adicionar Conda ao PATH
ENV PATH=/opt/conda/bin:$PATH

# Copiar os arquivos do projeto para o contêiner
COPY . .

# Criar e ativar o ambiente conda
RUN conda env create -f environment.yml && conda clean -a

# Instalar Samtools dentro do ambiente Conda
RUN /bin/bash -c "source activate metrics_app_env && \
    curl -L https://github.com/samtools/samtools/releases/download/1.19/samtools-1.19.tar.bz2 | tar -xj && \
    cd samtools-1.19 && \
    ./configure --prefix=/opt/conda/envs/metrics_app_env && \
    make && \
    make install && \
    cd .. && rm -rf samtools-1.19"

# Expor a porta do Streamlit
EXPOSE 8501

# Healthcheck para o Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Definir o entrypoint para o Streamlit
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "metrics_app_env", "streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
