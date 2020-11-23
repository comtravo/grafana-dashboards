FROM python:3

WORKDIR /opt/ct

COPY ./requirements.txt ./Makefile ./

RUN make init
