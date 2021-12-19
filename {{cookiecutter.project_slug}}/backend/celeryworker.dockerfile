FROM python:3.7

WORKDIR /app/

ARG PYPI=pypi.doubanio.com
ENV TZ=Asia/Shanghai

RUN echo "[global]" > /etc/pip.conf && \
    echo "index-url = https://${PYPI}/simple" >> /etc/pip.conf && \
    echo "trusted-host = ${PYPI}" >> /etc/pip.conf && \
    python -m pip install -U pip && \
    python -m pip install wheel

# Install Poetry
RUN curl -sSL https://gitee.com/mirrors/poetry/raw/master/get-poetry.py -o get-poetry.py

# ARG HTTP_PROXY=hostname:port
# RUN export http_proxy="http://${HTTP_PROXY}" && https_proxy="http://${HTTP_PROXY}"

RUN cat get-poetry.py | POETRY_HOME=/opt/poetry POETRY_VERSION=1.1.12 python
RUN cd /usr/local/bin && ln -s /opt/poetry/bin/poetry
RUN POETRY_HOME=/opt/poetry poetry config virtualenvs.create false

# RUN unset http_proxy && unset https_proxy

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

# Allow installing dev dependencies to run tests
RUN POETRY_HOME=/opt/poetry poetry config repositories.pypi https://${PYPI}/simple
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

ENV C_FORCE_ROOT=1

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app

COPY ./app/worker-start.sh /worker-start.sh

RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]
