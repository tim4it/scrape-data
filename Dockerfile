# Dockerfile scraper

FROM postgres:latest
FROM python:3.8-slim-buster

WORKDIR /app

RUN pip3 install scrapy
RUN pip3 install psycopg2-binary

COPY . .

CMD ["sh", "-c", "scrapy crawl sreality & python3 web_server.py"]
