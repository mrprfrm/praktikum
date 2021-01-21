from fabric.api import local


PROJECT_NAME = 'praktikum'


def run(service_name):
    try:
        local(f'docker rm -f {PROJECT_NAME}_{service_name}')
    except:
        pass
    finally:
        local(f'docker-compose run --name {PROJECT_NAME}_{service_name} --service-ports --use-aliases fulltextsearch poetry run flask run --host=0.0.0.0 --port=8000')


def bash(service_name):
    local(f'docker exec -it {PROJECT_NAME}_{service_name} bash')


def shell(service_name):
    local(f'docker exec -it {PROJECT_NAME}_{service_name} poetry run flask shell')


def etl(path):
    local(f'docker exec -it {PROJECT_NAME}_fulltextsearch poetry run flask etl {path}')

def init_index(path=''):
    if path:
        local(f'docker exec -it {PROJECT_NAME}_fulltextsearch poetry run flask init-index --c {path}')
    else:
        local(f'docker exec -it {PROJECT_NAME}_fulltextsearch poetry run flask init-index')
