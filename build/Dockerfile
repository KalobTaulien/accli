FROM ubuntu:16.04
MAINTAINER Cody Hiar <codyfh@gmail.com>

# Needed for better experience in container terminal
ENV TERM=xterm-256color

# Update and install
RUN apt-get update && apt-get install -y \
      git \
      wget \
      # for cal utility
      bsdmainutils \
      # Python
      python3-dev \
      python3-pip

# Add the project requirements
ADD requirements.txt /opt/requirements.txt

# # Install the requirements, remove 3 for wagtail
RUN /bin/bash -c 'cd /opt \
      && pip3 install -r requirements.txt'

ADD config.json /opt/config.json

# change to /opt for the working directory, you should mount the local dir volume here
WORKDIR /opt

# Add the entry script
ADD entry.sh /opt/
RUN chmod 755 /opt/entry.sh
