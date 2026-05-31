FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app
COPY libs /app/libs
COPY services /app/services

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

CMD ["python", "-m", "uvicorn", "services.reservation.app:app", "--host", "0.0.0.0", "--port", "8001"]
