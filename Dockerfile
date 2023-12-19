# syntax=docker/dockerfile:1
FROM python:3.10-alpine

RUN apk add --no-cache  git

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
COPY config.json .
COPY main.py .

EXPOSE 5012

CMD ["python", "main.py"]
