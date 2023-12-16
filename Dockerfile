FROM alpine:3

# Prepare base system
RUN apk update && apk upgrade && \
    apk add python3 py3-pip pipx git 

# Install smahub
RUN mkdir -p /opt/smahub
WORKDIR /opt/smahub

RUN git clone --depth=1 --branch=main https://github.com/AnotherDaniel/smahub . && rm -fr .git*
RUN pipx install . --include-deps

# Debug server port
EXPOSE 5678

ADD run_smahub.sh /root/
RUN chmod +x /root/*
ENTRYPOINT ["/root/run_smahub.sh"]