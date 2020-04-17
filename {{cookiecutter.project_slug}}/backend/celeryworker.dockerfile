FROM alpine:3.11

RUN apk update
RUN apk add python3 curl
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN source $HOME/.poetry/env
RUN poetry export -f requirements.txt -o requirements.txt


FROM python:3.7

RUN pip install raven celery~=4.3 passlib[bcrypt] tenacity requests "fastapi>=0.47.0" emails pyjwt email-validator jinja2 psycopg2-binary alembic SQLAlchemy

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

ENV C_FORCE_ROOT=1

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app

COPY ./app/worker-start.sh /worker-start.sh

RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]
