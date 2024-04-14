FROM ubuntu:latest
MAINTAINER Andrei Duvakin 'andrei@duvakin.ru'
RUN apt update -y && \
    apt install -y python3 python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
