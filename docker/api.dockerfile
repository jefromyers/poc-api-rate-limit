FROM python:3.11.0-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /api
COPY ./api /api

RUN pip install --no-cache-dir -r requirements.txt
