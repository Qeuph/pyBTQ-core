# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.10 and necessary packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3.10-venv \
    build-essential cmake libleveldb-dev swig3.0 ninja-build pkg-config libboost-all-dev libsodium-dev libssl-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create a virtual environment and activate it
RUN python3.10 -m venv venv_btq
ENV PATH="/app/venv_btq/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install setuptools==50.3.2 \
    && pip install plyvel==1.3.0

# Copy over and install any additional requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Make port 19007 19008 19009 19010 19090 19091 52134
EXPOSE 19007 19008 19009 19010 19090 19091 52134

# Define environment variable
ENV NAME BTQ

# Create /root/.btq directory and config.yml file
RUN mkdir -p /root/.btq \
    && echo "public_api_server: \"0.0.0.0:19009\"\npublic_api_host: \"0.0.0.0\"\npublic_api_port: 19009" > /root/.btq/config.yml

# Command to run on container start
CMD ["/app/entrypoint.sh"]