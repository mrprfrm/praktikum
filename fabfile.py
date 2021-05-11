from fabric.api import local


def run(service_name):
    local(f'docker-compose run --rm --name praktikum_{service_name} --service-ports --use-aliases {service_name} poetry run flask run --host=0.0.0.0 --port=8000')


def bash(service_name):
    local(f'docker-compose exec {service_name} bash')


def shell(service_name):
    local(f'docker-compose run --rm --use-aliases {service_name} poetry run flask shell')


def initdb(service_name):
    local(f'docker-compose run --rm --use-aliases {service_name} poetry run flask db init')


def migrate(service_name):
    local(f'docker-compose run --rm --use-aliases {service_name} poetry run flask db migrate')


def upgrade(service_name):
    local(f'docker-compose run --rm --use-aliases {service_name} poetry run flask db upgrade')


def etl(path):
    local(f'docker exec -it praktikum_fulltextsearch poetry run flask etl {path}')


def init_index(path=''):
    if path:
        local(f'docker exec -it praktikum_fulltextsearch poetry run flask init-index --c {path}')
    else:
        local(f'docker exec -it praktikum_fulltextsearch poetry run flask init-index')


def init_admin_shema():
    local(f'cat admin/schema/create_schema.sql | docker exec -i praktikum_database psql postgres -U postgres')
    local(f'cat admin/schema/create_indexes.sql | docker exec -i praktikum_database psql postgres -U postgres')


def rundb():
    local(f'docker run --rm -p 5432:5432 --name praktikum_testdb -e POSTGRES_PASSWORD=postgres postgres:13')
