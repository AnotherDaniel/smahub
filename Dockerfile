FROM alpine:3

# Prepare base system
RUN apk update && apk upgrade && \
    apk add python3 py3-pip git 

# Install smahub
RUN mkdir -p /opt/smahub
WORKDIR /opt/smahub

RUN git clone --depth=1 --branch=main https://github.com/AnotherDaniel/smahub . && rm -fr .git*
#COPY . /opt/smahub
RUN pip3 install .

ADD run_smahub.sh /root/
RUN chmod +x /root/*
ENTRYPOINT ["/root/run_smahub.sh"]