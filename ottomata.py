import click
from click import echo, secho

# TODO: User CLI


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option()
def cli():
    pass

if __name__ == '__main__':
    print('Hello, World!')