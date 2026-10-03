# pyproject.toml requires Python 3.11 (">=3.11,<3.12"); the previous python3.10
# base image could not install the project.
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

LABEL maintainer="Dev Parikh"

WORKDIR /app/

# Install Poetry from PyPI at a pinned version (instead of piping a remote
# script into python).
ARG POETRY_VERSION=1.8.3
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

COPY ./app /app/app

# Do not run the API as root.
RUN useradd --system --no-create-home appuser && chown -R appuser /app
USER appuser
