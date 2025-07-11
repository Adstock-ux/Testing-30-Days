# 1) Base Python slim
FROM python:3.12-slim

# 2) Diretório de trabalho
WORKDIR /app

# 3) Copia só o requirements.txt pra cache do Docker
COPY requirements.txt .

# 4) Instala libs nativas e build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      python3-dev \
      libatlas-base-dev \
      libblas-dev \
      liblapack-dev \
      libffi-dev \
      libssl-dev \
      git && \
    rm -rf /var/lib/apt/lists/*

# 5) Cria o virtualenv
RUN python -m venv /opt/venv

# 6) Atualiza pip, setuptools e wheel e instala deps
RUN /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 7) Usa o venv por padrão
ENV PATH="/opt/venv/bin:$PATH"

# 8) Copia todo o código
COPY . .

# 9) Comando padrão
CMD ["python", "main.py"]
