FROM python:3.8.5-alpine

LABEL maintainer Francis J. Garcia <francisjgarcia94@gmail.com>

WORKDIR /usr/src/app

COPY ./app/requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "-u", "app.py" ]