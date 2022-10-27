FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry==1.1.13

COPY poetry.lock pyproject.toml /tmp/

RUN poetry export -f requirements.txt --output requirements.txt


FROM python:3.10-slim

WORKDIR /opt/

COPY --from=requirements-stage /tmp/requirements.txt /opt/requirements.txt

RUN pip install --no-cache-dir -r /opt/requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["uvicorn", "backend.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
