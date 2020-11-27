FROM golang:1.14-buster

COPY --from=hashicorp/terraform:0.12.29 /bin/terraform /bin/
COPY --from=cytopia/terraform-docs /usr/local/bin/terraform-docs /bin/

RUN apt-get update && apt-get -y install python3 python3-pip && go version && python --version && terraform version && terraform-docs version

WORKDIR /opt/ct

COPY ./requirements.txt ./Makefile ./

RUN make init
COPY . .

RUN make lint

