FROM python:3.10

ARG UNICODE_VERSION
ENV UNICODE_VERSION=${UNICODE_VERSION}

ARG ENV
ENV ENV=${ENV}

ARG REDIS_URL
ENV REDIS_URL=${REDIS_URL}

ARG RATE_LIMIT_PER_PERIOD
ENV RATE_LIMIT_PER_PERIOD=${RATE_LIMIT_PER_PERIOD}

ARG RATE_LIMIT_PERIOD_MINUTES
ENV RATE_LIMIT_PERIOD_MINUTES=${RATE_LIMIT_PERIOD_MINUTES}

ARG RATE_LIMIT_BURST
ENV RATE_LIMIT_BURST=${RATE_LIMIT_BURST}

WORKDIR /code
RUN pip install -U pip setuptools wheel
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
EXPOSE 80
COPY ./app /code/app 
RUN PYTHONPATH=/code/. python /code/./app/data/scripts/get_prod_data.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
