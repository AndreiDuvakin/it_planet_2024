FROM ubuntu:latest
MAINTAINER Andrei Duvakin 'andrei@duvakin.ru'
RUN apt update -y
RUN apt install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ['python']
CMD ['main.py']