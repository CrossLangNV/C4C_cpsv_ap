# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Packages from CrossLang
RUN pip3 install git+https://github.com/CrossLangNV/DGFISMA_RDF.git@e2712bbe48c2791f28d80d9f950c18fbfda8be29 \
    --ignore-installed beautifulsoup4

