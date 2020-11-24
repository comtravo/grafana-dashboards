FROM python:3

COPY --from=hashicorp/terraform:0.12.29 /bin/terraform /bin/

WORKDIR /opt/ct

COPY ./requirements.txt ./Makefile ./

RUN make init
