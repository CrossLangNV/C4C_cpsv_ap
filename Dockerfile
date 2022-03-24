# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y git build-essential

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# NLTK
RUN python -m nltk.downloader punkt

# Packages from CrossLang
RUN pip3 install git+https://github.com/CrossLangNV/DGFISMA_RDF.git@fb9e840b200d26c58ba1b38ba314ccad7cb708b7 \
    --ignore-installed beautifulsoup4

#ARG GIT_TOKEN
#RUN git clone https://${GIT_TOKEN}@github.com/CrossLangNV/C4C_term_extraction.git
ENV PYTHONPATH /app
