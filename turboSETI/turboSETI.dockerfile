# Code from https://github.com/rtraas/turboCLOUD/blob/master/Dockerfile

FROM python:latest
ARG DEBIAN_FRONTEND=noninteractive

ENV TERM xterm

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
RUN python3 -m install git+https://github.com/UCBerkeleySETI/turbo_seti
COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip3 install -r requirements.txt


RUN python3 -m pip install turbo-seti
