FROM python:3.9-slim

RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]
