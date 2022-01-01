FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app/

# Setup Pypi
ARG PYPI=pypi.doubanio.com
ENV TZ=Asia/Shanghai

RUN echo "[global]" > /etc/pip.conf && \
    echo "index-url = https://${PYPI}/simple" >> /etc/pip.conf && \
    echo "trusted-host = ${PYPI}" >> /etc/pip.conf && \
    python -m pip install -U pip && \
    python -m pip install wheel

# Install Poetry
ARG POETRY_CN_URL=https://gitee.com/featureoverload/poetry
ARG POETRY_VERSION=1.1.11

# download
RUN curl -sSL ${POETRY_CN_URL}/raw/master/get-poetry.py -o get-poetry.py
### [alternative] download manually, and copy to /tmp to build image
RUN curl -sSL ${POETRY_CN_URL}/attach_files/931744/download/poetry-1.1.1-linux.tar.gz -o /tmp/poetry-1.1.1-linux.tar.gz
# install
RUN POETRY_HOME=/opt/poetry python get-poetry.py --file /tmp/poetry-1.1.1-linux.tar.gz
RUN cd /usr/local/bin && ln -s /opt/poetry/bin/poetry
RUN POETRY_HOME=/opt/poetry poetry config virtualenvs.create false

# Install Image Environment
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

# Allow installing dev dependencies to run tests
RUN POETRY_HOME=/opt/poetry poetry config repositories.pypi https://${PYPI}/simple
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install -vvv --no-root ; else poetry install -vvv --no-root --no-dev ; fi"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

COPY ./app /app
ENV PYTHONPATH=/app
