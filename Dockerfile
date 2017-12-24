FROM tknerr/baseimage-ubuntu:14.04

RUN apt-get update -y
RUN apt-get install -y vim nano
RUN apt-get install -y python3 python3-pip python3-dev build-essential
RUN apt-get install -y mongodb git apache2 libapache2-mod-wsgi-py3

RUN pip3 install pymongo==3.4
RUN pip3 install mongoengine

RUN rm /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-available/000-default.conf
RUN mkdir -p /data/db
RUN chown -R mongodb:mongodb /data
RUN sed -i 's/journal=true/journal=false/g' /etc/mongodb.conf

COPY ./rePullet.conf /etc/apache2/sites-available/rePullet.conf
COPY . /var/www/repulletapp
RUN pip3 install -r /var/www/repulletapp/requirements.txt

