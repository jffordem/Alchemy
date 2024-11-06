from invoke import task

@task
def db_start(c):
    "invoke db-start"
    c.run('docker run -p 27017:27017 -d mongodb/mongodb-community-server')

@task
def db_load(c):
    "invoke db-load"
    c.run('flask db_load')

@task
def start(c):
    "invoke start"
    c.run('flask run')

@task
def docker_push(c):
    "invoke docker-push"
    c.run('docker tag alchemy:latest jffordem/alchemy:latest')
    c.run('docker push jffordem/alchemy:latest')
