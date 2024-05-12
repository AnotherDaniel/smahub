FROM alpine:3

# Prepare base system
RUN apk update && apk upgrade && \
    apk add tzdata python3 py3-pip pipx git

# Set up smahub folder
RUN mkdir -p /opt/smahub
WORKDIR /opt/smahub

# Clone smahub
# RUN git clone --depth=1 --branch=main https://github.com/AnotherDaniel/smahub . && rm -fr .git*
COPY . /opt/smahub

# Create the virtualenv
ENV VIRTUAL_ENV=.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install smahub deps
RUN pip install .

# Debug server port
EXPOSE 5678

ADD run_smahub.sh /root/
RUN chmod +x /root/*
ENTRYPOINT ["/root/run_smahub.sh"]