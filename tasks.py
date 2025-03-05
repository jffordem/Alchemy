from invoke import task

@task
def start(c):
    "invoke start"
    c.run('flask run')

@task
def docker_push(c):
    "invoke docker-push"
    c.run('docker tag alchemy:latest jffordem/alchemy:latest')
    c.run('docker push jffordem/alchemy:latest')
