FROM python:3.10-slim

RUN apt-get update && \
    apt-get install musl-dev -y

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]