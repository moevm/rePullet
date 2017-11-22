FROM ubuntu:latest
MAINTAINER Alexey Chirukhin "pr3sto1377@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python3 python3-pip python3-dev build-essential
COPY . /rePullet
WORKDIR /rePullet
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["__init__.py"]

