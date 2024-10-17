import click 

from cli.config import config


@click.group()
def cli():
    '''
        This is a command line interface for the project
    '''
    pass

cli.add_command(config)




if __name__ == '__main__':
    cli()