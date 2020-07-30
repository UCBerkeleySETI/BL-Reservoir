FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN docker-apt-install \
     python3-setuptools \
     python3-scipy \
     python3-matplotlib \
     python3-bitshuffle \
     python3-h5py \
     python3-pip \
     git \
     curl \
     wget

RUN pip3 install zmq tqdm pandas wget google-cloud-storage hdf5plugin numpy==1.16.4

# install gcsfuse
ENV GCSFUSE_REPO=gcsfuse-bionic
RUN echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update
RUN apt-get -y install gcsfuse
RUN apt-get install -y python3-venv python3-wheel
RUN mkdir /buckets
RUN mkdir /buckets/bl-scale

# set up virtual environments
RUN mkdir /code
COPY . /code/bl_reservoir
WORKDIR /code/bl_reservoir
RUN chmod 777 /code/bl_reservoir/setup_environments.sh
RUN sh /code/bl_reservoir/setup_environments.sh

# run server
WORKDIR /code
CMD python3 -m bl_reservoir.$ALG_SUB_PACKAGE.$ALG_NAME
# CMD python3 -m bl_reservoir.server
