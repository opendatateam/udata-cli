from ucli.api import pass_api
from ucli.cli import cli
from ucli.utils import header, label_arrow


@cli.command()
@pass_api
def status(api):
    '''Display current site status'''
    header(status.__doc__)
    site = api.get('site')
    label_arrow('Title', site['title'])
    label_arrow('Datasets', site['metrics']['datasets'])
    label_arrow('Reuses', site['metrics']['reuses'])
    label_arrow('Organizations', site['metrics']['organizations'])
    label_arrow('Users', site['metrics']['users'])
    label_arrow('Discussions', site['metrics']['discussions'])
