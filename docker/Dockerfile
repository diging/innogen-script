FROM ubuntu:20.04

RUN apt update && apt install -y cmake g++ wget unzip

WORKDIR /opencv
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.6.0.zip
RUN unzip opencv.zip
RUN mkdir -p build
WORKDIR build
RUN cmake  ../opencv-4.6.0/
RUN cmake --build .

RUN apt-get update
RUN apt-get install -y python3 && ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get install -y python3-pip
RUN pip install opencv-python
