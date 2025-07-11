# Use uma imagem oficial Python (slim)
FROM python:3.12-slim

# Cria diretório de trabalho
WORKDIR /app

# Copia só o requirements.txt e instala antes de copiar o código
COPY requirements.txt ./

# Cria o venv em /opt/venv e instala as dependências
RUN python -m venv /opt/venv \
 && /opt/venv/bin/python -m pip install --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Ajusta o PATH para usar o venv por padrão
ENV PATH="/opt/venv/bin:$PATH"

# Copia o resto do seu código
COPY . .

# Comando padrão para rodar seu bot
CMD ["python", "main.py"]
