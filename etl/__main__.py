import importlib

import click

from pipelines import Executor


@click.group()
def cli():
    pass

@click.command()
@click.argument('path')
def run(path):
    executor = Executor()
    spec = importlib.util.spec_from_file_location('pipelines', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    executor.run(module)

cli.add_command(run)

if __name__ == '__main__':
    cli()
