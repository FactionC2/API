# Largely taken from https://sebest.github.io/post/protips-using-gunicorn-inside-a-docker-image/

FROM alpine:3.11

# server specific variables
ENV GUNICORN_SERVER gunicorn
ENV GUNICORN_WORKER_CLASS eventlet
ENV GUNICORN_WORKERS 1
ENV GUNICORN_LOGGING_CONFIG /app/logging.conf
# if developing, set timeout to something low like 3 or 5
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_BIND_ADDRESS 0.0.0.0
ENV GUNICORN_BIND_PORT 5000
ENV GUNICORN_DEBUG 0
ENV GUNICORN_RELOAD 0
ENV GUNICORN_OPTS ""

# api variables
ENV API_UPLOAD_DIR /opt/faction/uploads
ENV POSTGRES_HOST db
ENV POSTGRES_DATABASE faction
ENV POSTGRES_USERNAME postgres
ENV RABBIT_HOST mq
ENV RABBIT_USERNAME guest
ENV USE_NATIVE_LOGGER 0
# this is only used when GUNICORN_SERVER is "flask"
ENV DEFAULT_LOGGING_LEVEL INFO

# api secrets: leave these uncommented so that the user is forced to set them
# ENV FLASK_SECRET ""
# ENV POSTGRES_PASSWORD ""
# ENV RABBIT_PASSWORD ""

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

# symlink to expose "python" command
RUN ln -s /usr/bin/python3 /usr/bin/python

# make default upload directory
RUN mkdir -p /opt/faction/uploads

RUN mkdir /app
WORKDIR /app

RUN addgroup -S -g 1337 gunicorn && \
    adduser -S -G gunicorn -u 1337 gunicorn && \
    pip3 install --upgrade pip  && \
    pip3 install pipenv && \
    mkdir -p ./cache && \
    chown gunicorn:gunicorn ./cache

# add Pipfile and install dependencies before adding /app
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system

# add and configure startup.sh file
COPY startup.sh /opt/startup.sh 
RUN chmod +x /opt/startup.sh
RUN chown gunicorn:gunicorn /opt/startup.sh

# give gunicorn control over default upload path
RUN chown gunicorn:gunicorn /opt/faction/uploads

# add core app files
COPY ./docker_build/logging.conf /app/logging.conf
ADD . /app
RUN chmod +x /app/app.py

EXPOSE 5000

USER gunicorn

ENTRYPOINT ["/opt/startup.sh"]