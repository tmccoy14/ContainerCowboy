# Ubuntu Image
FROM ubuntu:18.04

# Install packages
RUN apt-get update && apt-get install -y \
    wget \
    python3-pip \
    git \
    golang

# Install AWS CLI Tool
RUN pip3 install awscli

# Create project directory
RUN mkdir /containercowboy
WORKDIR /containercowboy
ADD . /containercowboy/
RUN pip3 install -r requirements.txt

# Authenticate with AWS
RUN chmod +x auth.sh
RUN ./auth.sh

# Run application
RUN python3 app.py