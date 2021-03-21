from fabric.api import local


PROJECT_NAME = 'praktikum'


def run(service_name):
    try:
        local(f'docker rm -f {PROJECT_NAME}_{service_name}')
    except:
        pass
    finally:
        local(f'docker-compose run --name {PROJECT_NAME}_{service_name} --service-ports --use-aliases {service_name} poetry run flask run --host=0.0.0.0 --port=8000')


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


def init_admin_shema():
    local(f'cat admin/schema/create_schema.sql | docker exec -i {PROJECT_NAME}_database psql postgres -U postgres')
    local(f'cat admin/schema/create_indexes.sql | docker exec -i {PROJECT_NAME}_database psql postgres -U postgres')


def rundb():
    local(f'docker run --rm -p 5432:5432 --name {PROJECT_NAME}_testdb -e POSTGRES_PASSWORD=postgres postgres:13')
