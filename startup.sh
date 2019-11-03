#!/bin/sh

# allow the application dir to be overidden to run locally
GUNICORN_API_DIR=${GUNICORN_API_DIR:-/app}

function gunicorn_run() {
    # define default opts
    gunicorn_bind_address="${GUNICORN_BIND_ADDRESS:-0.0.0.0}";
    gunicorn_bind_port="${GUNICORN_BIND_PORT:-5000}";
    gunicorn_bind="${gunicorn_bind_address}:${gunicorn_bind_port}";

    # flask socketio may have restrictions on workers, default to 1
    gunicorn_workers="${GUNICORN_WORKERS:-1}";

    # set to low value like 3 or 5 to get reloading working
    gunicorn_timeout="${GUNICORN_TIMEOUT:-20}";
    
    # combine default opts
    gunicorn_opts="--workers $gunicorn_workers --timeout $gunicorn_timeout --bind $gunicorn_bind";

    # define and set option opts
    # allow the ability to worker_class and log_config to empty string to skip options
    gunicorn_worker_class="${GUNICORN_WORKER_CLASS}";
    if [ ${#gunicorn_worker_class} -gt 0 ]; then
        gunicorn_opts="$gunicorn_opts --worker-class $gunicorn_worker_class";
    fi

    gunicorn_logging_config="${GUNICORN_LOGGING_CONFIG}";
    if [ ${#gunicorn_logging_config} -gt 0 ]; then
        gunicorn_opts="$gunicorn_opts --log-config $gunicorn_logging_config";
    fi

    # configure debug/reloading
    gunicorn_reload="${GUNICORN_RELOAD:-0}";
    gunicorn_debug="${GUNICORN_DEBUG:-0}";
    if [ "${gunicorn_debug}" == "1" ]; then
        gunicorn_opts="$gunicorn_opts --reload";
    elif [ "${gunicorn_reload}" == "1" ]; then
        gunicorn_opts="$gunicorn_opts --reload";
    fi

    # set custom options
    if [ ${#GUNICORN_OPTS} -gt 1 ]; then
        gunicorn_opts="${gunicorn_opts} ${GUNICORN_OPTS}";
    fi

    echo "Gunicorn Options: $gunicorn_opts";
    echo "Starting gunicorn...";
    exec gunicorn $gunicorn_opts app:app;
}

if [ ${#@} -gt 0 ]; then
    # if arguments are passed in, just run the commands
    $@
else
    echo "API Server: ${GUNICORN_SERVER}...";

    if [ "$GUNICORN_SERVER" == "flask" ]; then
        echo "Starting ${GUNICORN_API_DIR}/app.py...";
        exec ${GUNICORN_API_DIR}/app.py;
    else
        gunicorn_run;
    fi
fi