FROM python:3.9-slim

RUN mkdir /project

COPY requirements.txt /project

RUN python -m pip install -r /project/requirements.txt

COPY not_twitter /project/not_twitter

ENV PYTHONPATH "$PYTHONPATH:/project"

WORKDIR project/not_twitter/app

CMD uvicorn main:app --host 0.0.0.0 --port 5000
