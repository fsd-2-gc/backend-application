FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps voor mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev pkg-config \
 && rm -rf /var/lib/apt/lists/*

# Dependencies installeren
COPY docker-tankalyze-api/web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projectcode kopiëren
COPY . .

# Entrypoint
RUN chmod +x docker-tankalyze-api/web/entrypoint.sh
ENTRYPOINT ["docker-tankalyze-api/web/entrypoint.sh"]

EXPOSE 8000
