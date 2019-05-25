# Largely taken from https://sebest.github.io/post/protips-using-gunicorn-inside-a-docker-image/

FROM alpine:3.8
RUN apk add --no-cache \
            python3 \
            py3-gunicorn \
            python3-dev \
            g++ \
            make \
            libffi-dev \
            libcap \
            musl-dev \
            gcc \
            postgresql-dev
ADD . /app
WORKDIR /app
COPY ./docker_build/logging.conf /app/logging.conf
RUN addgroup -S -g 1337 gunicorn && \
    adduser -S -G gunicorn -u 1337 gunicorn && \
    pip3 install --upgrade pip  && \
    pip3 install pipenv  && \
    pipenv install --system && \
    mkdir -p ./cache && \
    chown gunicorn:gunicorn ./cache
EXPOSE 5000

USER gunicorn
CMD ["/usr/bin/gunicorn", \
  "--worker-class", "eventlet", \
  "--workers", "1", \
  "--log-config", "/app/logging.conf", \
  "--timeout", "300", \
  "--bind", "0.0.0.0:5000", \
  "app:app" ]
