import click

from .api import Api
from .log import init_logging


CONTEXT_SETTINGS = {
    'auto_envvar_prefix': 'UDATA',
    'help_option_names': ['-?', '-h', '--help'],
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--url', envvar='URL', default='http://localhost:7000',
              help='The UData instance URL')
@click.option('--token', envvar='TOKEN', help='Your UData API Key')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--ssl-check/--no-ssl-check', default=True,
              help='Disable SSL validation (for testing purpose)')
@click.pass_context
def cli(ctx, url, token, verbose, **kwargs):
    '''UData remote client'''
    init_logging(verbose)
    ctx.obj = Api(url, token, **kwargs)


# Import commands
import ucli.commands.me  # noqa
import ucli.commands.dispatch  # noqa
import ucli.commands.status  # noqa
import ucli.commands.transfer  # noqa
import ucli.commands.datasets.delete  # noqa
