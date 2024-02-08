# syntax=docker/dockerfile:1

FROM alpine:latest

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN uvicorn main:app --reload