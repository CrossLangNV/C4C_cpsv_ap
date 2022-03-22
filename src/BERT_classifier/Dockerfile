FROM ubuntu:18.04

MAINTAINER arne <arnedefauw@gmail.com>

ARG MODEL_DIR

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl && \
    apt-get clean

# Install miniconda to /miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda install -y python=3.8 && \
conda install pytorch==1.7.0 cpuonly -c pytorch && \
conda clean --all

#Install gcc
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /work
