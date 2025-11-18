FROM python:3.9-slim

ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2

RUN apt-get update \
 && apt-get install -y --no-install-recommends redis-server redis-tools tini ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY redis.conf /etc/redis/redis.conf
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

VOLUME ["/data"]

ENTRYPOINT ["tini","--"]
CMD ["/app/start.sh"]
