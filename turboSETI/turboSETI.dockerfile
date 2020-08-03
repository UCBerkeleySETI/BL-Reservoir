FROM python:latest
ARG DEBIAN_FRONTEND=noninteractive

ENV TERM xterm

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
COPY requirements.txt /tmp
COPY requirements_git.txt /tmp
WORKDIR /tmp
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_git.txt

RUN python3 -m pip install turbo-seti
