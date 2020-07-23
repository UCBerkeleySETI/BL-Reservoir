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

RUN mkdir /code
COPY . /code/bl_reservoir
WORKDIR /bl_reservoir
RUN setup_environments.sh

CMD /code/bl_reservoir/$ALG_SUB_PACKAGE/${ALG_SUB_PACKAGE}_env/bin/python3 -m bl_reservoir.$ALG_SUB_PACKAGE.$ALG_NAME
