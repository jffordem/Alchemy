from invoke import task

@task
def start(c):
    "invoke start"
    c.run('flask run')

@task
def start_debug(c):
    "invoke start-debug"
    c.run('flask run --debugger --reload')

@task
def docker_build(c):
    "invoke docker-build"
    c.run('docker build -t alchemy .')

@task
def docker_run(c):
    "invoke docker-run"
    c.run('docker run -p 8088:8088 -d alchemy')

@task
def docker_push(c):
    "invoke docker-push"
    c.run('docker tag alchemy:latest jffordem/alchemy:latest')
    c.run('docker push jffordem/alchemy:latest')

@task(help={
    'verbose': 'Show verbose test output (-v flag)',
    'failfast': 'Stop on first failure (-x flag)',
    'markers': 'Only run tests with specific markers (e.g., "not webtest")'
})
def test(c, verbose=False, failfast=False, markers=None):
    """Run pytest unit tests"""
    command = ['pytest']
    if verbose:
        command.append('-v')
    if failfast:
        command.append('-x')
    if markers:
        command.append(f'-m "{markers}"')
    
    c.run(' '.join(command))
