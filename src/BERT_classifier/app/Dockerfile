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

RUN pip install \
torchtext==0.8.0 \
scikit-learn==0.23.2 \
scikit-multilearn==0.2.0 \
transformers==3.4.0 \
numpy==1.18.5 \
pandas==1.2.4 \
pytest==6.1.1 \
fastapi==0.61.1 \
uvicorn==0.12.1

WORKDIR /work

#copy code:
COPY app.py /work
COPY trainer_bert_sequence_classifier.py /work
COPY read_data.py /work
COPY utils.py /work

#copy model:
COPY $MODEL_DIR/*.bin /work/models/pytorch_model.bin
COPY $MODEL_DIR/config.json /work/models/
COPY $MODEL_DIR/vocab.txt /work/models/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

#CMD python /work/app.py