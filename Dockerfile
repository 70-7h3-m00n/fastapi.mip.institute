FROM python:3.11-slim-buster

ENV CURL_CA_BUNDLE="" \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip --quiet --no-cache-dir install --upgrade pip poetry==1.2.2 poetry-core==1.3.2

COPY ./pyproject.toml ./poetry.lock /

RUN poetry install --no-interaction --no-ansi

ENV PATH="${PATH}:/root/.local/bin"

COPY ./scripts/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && \
    chmod +x /entrypoint

COPY ./scripts/start /start
RUN sed -i 's/\r$//g' /start && \
    chmod +x /start

ENV PYTHONPATH /app
WORKDIR /app

COPY . .

EXPOSE 8000

ENTRYPOINT ["/entrypoint"]
CMD ["uvicorn", "app.main:app", "--port=8000", "--host=0.0.0.0"]
