#------------------------------------------------------------------------------------------------------------------------------
# Dockerfile to install the remote host Docker image for Pegasus WMS pegasus-aws-batch.
#
# Component of: Titan2D Hazard Map Emulator Workflow
# Purpose: Run a Pegasus WMS workflow on Amazon AWS
# Author: Renette Jones-Ivey
# Date: July 2026
# Important: need to source ../pegasus-wms-configuration-scripts/configure.sh before building the remotehostimage Docker image.
# See ../pegasus-wms-configuration-scripts/configure.sh for more information.
#
# When the remotehostimage Docker image is created or updated,
# need to upload the image to the Amazon Elastic Container Registry (ECR) repository.
# See ./push-remotehostimage-to-ECR.sh for more information.

#-------------------------------------------------------------------------------------------------------------------------------

# References:
#
# https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html#
# https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job
# https://github.com/jsperhac/titan2d-docker

# https://docs.docker.com/engine/reference/commandline/build/
# --tag,-t Name
# build:
#   # docker builder prune to remove cache first
#   docker image build -t ghubtoolsremotehostimage . 2>&1 | tee build.log

# ====================================================================
# System installations
# ====================================================================

# Rocky Linux is an open-source enterprise operating system compatible with Red Hat Enterprise Linux.
FROM rockylinux:8
LABEL desc="remotehost Docker image for Pegasus WMS pegasus-aws-batch."

# Core count for compilation
ENV NUM_PROCESSES=4

RUN dnf -y update && \
    dnf -y install 'dnf-command(config-manager)' && \
    dnf -y config-manager --set-enabled powertools && \
    dnf -y config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo && \
    dnf -y install epel-release

# gcc, gcc-c++ plus others
RUN dnf -y groupinstall "Development Tools"

# Note: perl findutils, aws cli, unzip and futures required for pegasus-aws-batch

RUN dnf -y install --allowerasing --nobest \
    autoconf \
    automake \
    gcc-gfortran \
    git \
    make \
    perl findutils \
    python3-devel \
    python3-pip \
    R \
    sudo \
    swig \
    wget \
    which \
    unzip \
    zlib*

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN sudo ./aws/install

# ====================================================================
# Octave installation
# ====================================================================

# Reverified on Sept 12, 2024, the default version of Octave installed is version 5.2.0.
RUN dnf -y install --allowerasing --nobest \
     octave \
     octave-devel

ADD ./remotehost/fetch_and_run.sh /usr/local/bin/fetch_and_run.sh

USER root
RUN ln -s /usr/bin/python3.6 /usr/bin/python

WORKDIR /tmp
USER nobody
ENTRYPOINT ["/usr/local/bin/fetch_and_run.sh"]
