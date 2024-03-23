FROM quocbao747/bittensor:1.0

# For healthcheck
#RUN apk --update --no-cache add curl

WORKDIR /app

# This take time. In case having changes in requirements.txt, we don't
# need to rebuild docker image with bittensor
# RUN pip3 install --no-cache-dir bittensor

COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#ADD data /app/data
#ADD api /app/api
#ADD common /app/common
#ADD core /app/core

COPY bittensor_http_api.py /app
COPY config.py /app

CMD [ "gunicorn", "--access-logfile", "-", "-c", "config.py", "wsgi:bittensor_http_api"]
