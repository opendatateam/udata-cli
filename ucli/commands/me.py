from ucli.api import pass_api
from ucli.cli import cli
from ucli.utils import header, label_arrow


@cli.command()
@pass_api
def me(api):
    '''Display my user information'''
    header(me.__doc__)
    data = api.get('me')
    label_arrow('Name', '{first_name} {last_name}'.format(**data))
    label_arrow('ID', data['id'])
    label_arrow('Email', data['id'])
    label_arrow('Roles', ','.join(data['roles']))

    orgs = '\n'.join('    🏢 {name}'.format(**org) for org in data['organizations'])
    label_arrow('Organizations', '\n{0}'.format(orgs))
