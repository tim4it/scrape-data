# Scrape data from website example
Use `scrapy` framework to scrape the first 500 items (title, image url) from `sreality.cz` (flats, sell) and save it in the `Postgresql` database. Implement a simple HTTP server in python and show these 500 items on a simple page (title and image) and put everything to single docker-compose command so that we can run `docker-compose up` and see the scraped ads on http://localhost:8080 page.

## Docker related stuff

Inside docker:
```
docker exec -ti {container id} bash
```
Docker view:
```
docker ps -a
```
Docker images:
```
docker images -a
docker image ls
```
Docker images remove:
```
docker image rm {container id}
```
Remove dangling images:

List:
```
docker images -f dangling=true
```
Remove:
```
docker image prune
```

## Docker compose

Build with no cache:
```
docker-compose build --no-cache
```
Compose with build:
```
docker-compose up --build
```
Compose:
```
docker-compose up
docker-compose down
```

## Run application

```
docker-compose up
```
Start web browser and type:
```
http://localhost:8080/
```

## Application dynamic records

In the code we can change constant '**estate size**':
```
ESTATE_RECORDS_SIZE
```
Default is set to 500, but we can change to any number larger than 0. This will show number of item inserted and presented in html view. When code change is made, we must execute **docker-compose** again to get new version of data and view:
```
docker-compose down
docker-compose up --build
```
or:
```
docker-compose down
docker-compose build --no-cache
docker-compose up
```
