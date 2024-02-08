# syntax=docker/dockerfile:1

FROM python:3.10.10-alpine

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN python --version

COPY requirements.txt /usr/src/app/
COPY main.py /usr/src/app/

RUN pip install -r requirements.txt

#RUN export UVICORN_PORT=$`PORT`
RUN export `PORT`=8000

EXPOSE 8000

RUN uvicorn main:app --reload --host 0.0.0.0 --workers 2