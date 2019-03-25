docker container rm -f alchemy
docker image rm alchemy
docker build --tag=alchemy .
docker run -d --name alchemy -p 8080:80 alchemy
docker logs alchemy -f