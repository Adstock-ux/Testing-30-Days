# 1) Base Python slim
FROM python:3.12-slim

# 2) Set workdir
WORKDIR /app

# 3) Copia só o requirements pra aproveitar cache do Docker
COPY requirements.txt .

# 4) Instala compiladores e libs nativas essenciais
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libatlas-base-dev \
      libblas-dev \
      liblapack-dev \
      libffi-dev \
      libssl-dev \
      git && \
    rm -rf /var/lib/apt/lists/*

# 5) (Opcional) Criar e usar um virtualenv
RUN python -m venv /opt/venv

# 6) Atualiza pip e instala as deps — dentro do venv
RUN /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 7) Ajusta PATH para usar o venv por padrão
ENV PATH="/opt/venv/bin:$PATH"

# 8) Copia seu código
COPY . .

# 9) Comando default
CMD ["python", "main.py"]
