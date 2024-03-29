FROM python:3.9-slim

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app/ /app/

WORKDIR /app/api

CMD ["uvicorn" , "main:app", "--host", "0.0.0.0", "--port", "80"]