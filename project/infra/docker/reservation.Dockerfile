FROM python:3.12-slim

WORKDIR /app
COPY . /app

CMD ["python", "-m", "uvicorn", "services.reservation.app:app", "--host", "0.0.0.0", "--port", "8001"]
