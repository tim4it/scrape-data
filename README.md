# Scrape data
Scrape data from net and put some data to postgres

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
