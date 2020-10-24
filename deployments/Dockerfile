FROM python:3.8.5-slim-buster

LABEL version="1.0"

LABEL maintainer Francis J. Garcia <francisjgarcia94@gmail.com>

RUN ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

COPY ./app/requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

WORKDIR /usr/src/app

CMD [ "python", "-u", "app.py" ]
