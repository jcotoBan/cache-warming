FROM python:3.9-slim-buster
WORKDIR /app
COPY crawler.py /app/crawler.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y wget
EXPOSE 5005
ENTRYPOINT ["python", "crawler.py"]