FROM python:2.7.14
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat
RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /code/

