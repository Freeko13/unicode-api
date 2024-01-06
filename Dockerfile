FROM python:3.11

ARG ENV
ARG UNICODE_VERSION
ARG REDIS_HOST
ARG REDIS_PORT
ARG REDIS_DB
ARG REDIS_PW
ARG RATE_LIMIT_PER_PERIOD
ARG RATE_LIMIT_PERIOD_SECONDS
ARG RATE_LIMIT_BURST
ARG TEST_HEADER
ARG TEST1
ARG TEST2

ENV ENV=${ENV}
ENV UNICODE_VERSION=${UNICODE_VERSION}
ENV REDIS_HOST=${REDIS_HOST}
ENV REDIS_PORT=${REDIS_PORT}
ENV REDIS_DB=${REDIS_DB}
ENV REDIS_PW=${REDIS_PW}
ENV RATE_LIMIT_PER_PERIOD=${RATE_LIMIT_PER_PERIOD}
ENV RATE_LIMIT_PERIOD_SECONDS=${RATE_LIMIT_PERIOD_SECONDS}
ENV RATE_LIMIT_BURST=${RATE_LIMIT_BURST}
ENV TEST_HEADER=${TEST_HEADER}
ENV TEST1=${TEST1}
ENV TEST2=${TEST2}

WORKDIR /code
RUN pip install -U pip setuptools wheel
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
EXPOSE 80
COPY ./app /code/app 

RUN echo REDIS_PW: $REDIS_PW
RUN echo TEST1: $TEST1
RUN echo TEST2: $TEST2

RUN PYTHONPATH=/code/. python /code/./app/data/scripts/get_prod_data.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
