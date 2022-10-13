FROM python:3.10-slim
MAINTAINER painassasin@icloud.com

WORKDIR /opt/

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHON_PATH=/opt/todolist \
    POETRY_VERSION=1.1.13

RUN groupadd --system service && useradd --system -g service api

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml ./
RUN  poetry config virtualenvs.create false \
     && poetry install --no-root --no-dev --no-ansi --no-interaction

COPY . .

USER api

EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["uvicorn", "backend.app:create_app", "--factory","--reload", "--host", "0.0.0.0", "--port", "8000"]
