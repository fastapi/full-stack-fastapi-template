FROM python:3.7 AS python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
FROM python-base AS celery-worker
ENV C_FORCE_ROOT=1

RUN pip install raven celery~=4.3 passlib[bcrypt] tenacity requests "fastapi>=0.16.0" emails pyjwt email_validator jinja2 psycopg2-binary alembic SQLAlchemy


COPY ./app /app
WORKDIR /app

COPY ./app/worker-start.sh /worker-start.sh
RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
FROM python-base AS backend-tests

RUN pip install requests pytest tenacity passlib[bcrypt] "fastapi>=0.16.0" psycopg2-binary SQLAlchemy

COPY ./app /app

COPY ./app/tests-start.sh /tests-start.sh
RUN chmod +x /tests-start.sh

# This will make the container wait, doing nothing, but alive
CMD ["bash", "-c", "while true; do sleep 1; done"]

# Afterwards you can exec a command /tests-start.sh in the live container, like:
# docker exec -it backend-tests /tests-start.sh



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7 AS backend
ENV PYTHONPATH=/app

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

RUN pip install celery~=4.3 passlib[bcrypt] tenacity requests emails "fastapi>=0.47.0" "uvicorn>=0.11.1" gunicorn pyjwt python-multipart email_validator jinja2 psycopg2-binary alembic SQLAlchemy

COPY ./app /app
WORKDIR /app/

EXPOSE 80
