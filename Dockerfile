FROM quocbao747/bittensor:1.0

# For healthcheck
#RUN apk --update --no-cache add curl

WORKDIR /bittensor_http_api

# This take time. In case having changes in requirements.txt, we don't
# need to rebuild docker image with bittensor
# RUN pip3 install --no-cache-dir bittensor

COPY bittensor_http_api/requirements.txt /bittensor_http_api
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY bittensor_http_api/ /bittensor_http_api/

EXPOSE 8080

CMD [ "gunicorn", "--timeout", "900", "--access-logfile", "-", "-c", "config.py", "wsgi:bittensor_http_api"]
