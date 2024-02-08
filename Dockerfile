# syntax=docker/dockerfile:1

FROM alpine:latest

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN uvicorn main:app --reload