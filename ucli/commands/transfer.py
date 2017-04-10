import logging

from textwrap import dedent

import click

from ucli import suggest
from ucli.api import pass_api
from ucli.cli import cli
from ucli.utils import header, prompt_choices, choice_enum, label_arrow, white, success

log = logging.getLogger(__name__)


TYPE_CHOICES, (IS_DATASET, IS_REUSE) = choice_enum('Dataset', 'Reuse')

ADMIN_SOURCE_CHOICES, (MINE, MY_ORGS, ANY_USER, ANY_ORG) = choice_enum(
    'Mine',
    'My organizations',
    'Any user',
    'Any organization',
)

SOURCE_CHOICES = ADMIN_SOURCE_CHOICES[:2]

TARGET_CHOICES, (AN_USER, AN_ORG) = choice_enum('An user', 'An Organization')


@cli.command()
@pass_api
def transfer(api):
    '''Massive datasets or reuses transfer'''
    header(transfer.__doc__)
    me = api.get('me')
    is_admin = 'admin' in me['roles']

    # Prompt user for object type
    type_choice = prompt_choices('Transfer types', *TYPE_CHOICES)

    # Prompt user for source
    source_choices = ADMIN_SOURCE_CHOICES if is_admin else SOURCE_CHOICES
    source_choice = prompt_choices('Transfer from ?', *source_choices)
    if source_choice == MY_ORGS:
        org_choices = enumerate((o['name'] for o in me['organizations']), 1)
        org_choice = prompt_choices('Your organizations', *org_choices)
        org_index = int(org_choice) - 1
        source = me['organizations'][org_index]
    elif source_choice == ANY_USER:
        source = suggest.users(api)
    elif source_choice == ANY_ORG:
        source = suggest.organizations(api)

    # Prompt user for target
    target_choice = prompt_choices('Target types', *TARGET_CHOICES)
    if target_choice == AN_USER:
        target = suggest.users(api)
    elif target_choice == AN_ORG:
        target = suggest.organizations(api)

    # Prompt user for message
    message = click.prompt('Please enter the transfer reason')

    # Fetch items
    qs = {'owner': source['id']} if source_choice in (MINE, ANY_USER) else {'organization': source['id']}
    qs['page_size'] = '1000'  # Try to fetch once
    endpoint = 'datasets/' if type_choice == IS_DATASET else 'reuses/'
    items = api.get(endpoint, fields='data{id,slug,title,owner,organization},total', **qs)

    # Display a summary and ask for confirmation
    if source_choice == MINE:
        source_label = 'your user'
    elif source_choice in (MY_ORGS, ANY_ORG):
        source_label = '"{name}" organization'.format(**source)
    else:
        source_label = '"{first_name} {last_name}" user'.format(**source)
    if target_choice == AN_ORG:
        target_label = '"{name}" organization'.format(**target)
    else:
        target_label = '"{first_name} {last_name}" user'.format(**target)
    label_arrow('Summary', dedent('''
    Will transfer all {type} ({total}) from {source} to {target}.
    The transfer reason is: {message}''').format(
        type=white('datasets' if type_choice == IS_DATASET else 'reuses'),
        source=white(source_label),
        target=white(target_label),
        message=message,
        total=white(items['total']),
    ))
    click.confirm('Are you sure ?', abort=True)

    # Perform
    item_type = 'Dataset' if type_choice == IS_DATASET else 'Reuse'
    for item in items['data']:
        log.info('Transfering %s(%s)', item_type, item['id'])
        request_payload = {
            'comment': message,
            'recipient': {
                'class': 'Organization' if target_choice == AN_ORG else 'User',
                'id': target['id'],
            },
            'subject': {
                'class': item_type,
                'id': item['id'],
            }
        }

        request_response = api.post('transfer/', request_payload)

        accept_payload = {
            'response': 'accept',
            'comment': 'Automatically accepted by udata-cli',
        }

        transfer_url = 'transfer/{id}/'.format(**request_response)
        accept_reponse = api.post(transfer_url, accept_payload)

        msg = (
            '{subject[class]}({subject[id]}) '
            'transfered to '
            '{recipient[class]}({recipient[id]})'
        ).format(**accept_reponse)
        log.info(msg)

    success('Transfered {0} item(s)'.format(items['total']))
