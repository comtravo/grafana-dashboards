FROM comtravo/terraform:test-workhorse-0.14.11-1.0.0

WORKDIR /opt/ct

RUN apt-get update && apt-get -y install python3 python3-pip jq && go version && python3 --version && terraform version && terraform-docs version

COPY ./requirements.txt ./Makefile ./

RUN make init
COPY . .

