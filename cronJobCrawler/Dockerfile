FROM python:3.9-slim-buster
WORKDIR /app
COPY cjcrawler.py /app/cjcrawler.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y wget && apt-get install -y curl
ENTRYPOINT ["python", "cjcrawler.py"]