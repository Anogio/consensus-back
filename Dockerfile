# https://hub.docker.com/_/python
FROM python:3.11-slim-bullseye

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app

WORKDIR /app
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
