FROM ubuntu:18.04

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y apt-utils python3 \
 python3-pip \
 python3-dev \
 python-opencv \
 libhdf5-serial-dev \
 gfortran \
 pkg-config \
 git curl wget \
 libomp-dev


RUN pip3 install wheel setuptools scipy matplotlib Cython cmake


RUN pip3 install zmq tqdm pandas wget google-cloud-storage hdf5plugin numpy==1.16.4

# make sure we have the compiler for C
RUN apt-get install -y build-essential

# HDF5 fixup
# Ubuntu 16.04 has a crazy hdf5 setup, needs some massaging, and extra flags to install h5py
ENV CFLAGS="-I/usr/include/hdf5/serial -L/usr/lib/x86_64-linux-gnu/hdf5/serial"
RUN ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial.so /usr/lib/x86_64-linux-gnu/libhdf5.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial_hl.so /usr/lib/x86_64-linux-gnu/libhdf5_hl.so

RUN pip3 install git+https://github.com/kiyo-masui/bitshuffle

# install gcsfuse
ENV GCSFUSE_REPO=gcsfuse-bionic
RUN echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update
RUN apt-get install -y gcsfuse
RUN apt-get install -y python3-venv python3-wheel
RUN mkdir /buckets
RUN mkdir /buckets/bl-scale
RUN mkdir /results_buffer

# set up virtual environments
RUN mkdir /code
COPY . /code/bl_reservoir
WORKDIR /code/bl_reservoir
RUN chmod 777 /code/bl_reservoir/setup_environments.sh
RUN sh /code/bl_reservoir/setup_environments.sh

# run server
WORKDIR /code
# CMD python3 -m bl_reservoir.$ALG_SUB_PACKAGE.$ALG_NAME
CMD sh start_server.sh
