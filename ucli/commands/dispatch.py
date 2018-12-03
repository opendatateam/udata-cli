import csv
import logging

from textwrap import dedent

import click

from ucli.api import pass_api
from ucli.cli import cli
from ucli.utils import header, prompt_choices, choice_enum, label_arrow, white, success, WARNING, yellow

log = logging.getLogger(__name__)


TYPE_CHOICES, (IS_DATASET, IS_REUSE) = choice_enum('Dataset', 'Reuse')

TARGET_CHOICES, (ORG_TARGET, USER_TARGET) = choice_enum('Organizations', 'Users')


@cli.command()
@click.option('--dryrun', '-d', is_flag=True)
@click.option('--force', '-f', is_flag=True)
@click.argument('file', type=click.File('r', encoding='utf8'))
@pass_api
def dispatch(api, file, dryrun, force):
    '''Dispatch datasets to organizations given a CSV file (with dataset and recipient IDs)'''
    header(dispatch.__doc__)
    me = api.get('me')
    is_admin = 'admin' in me['roles']

    dialect = csv.Sniffer().sniff(file.read(1024))
    file.seek(0)
    reader = csv.DictReader(file, dialect=dialect)
    rows = list(reader)

    choices = list(enumerate(reader.fieldnames))

    # Prompt user for object type
    response = prompt_choices('Item ID column', *choices)
    item_col = reader.fieldnames[int(response)]
    item_type = prompt_choices('Item type', *TYPE_CHOICES)

    response = prompt_choices('Target column', *choices)
    target_col = reader.fieldnames[int(response)]
    target_type = prompt_choices('Target type', *TARGET_CHOICES)

    message = click.prompt('Please enter the transfer reason')
    warning = ''

    if not is_admin:
        warning = ' '.join((
            yellow(WARNING),
            'You are not admin, this will create a transfer request for each item '
            'if you are not allowed to accept the transfer.\n'
        ))

    # Display a summary and ask for confirmation
    label_arrow('Summary', dedent('''
    Will transfer all {type} ({total})
        designated by the {item_col} column
        from {source}
        to {target_type} designated by the {target_col} column.
    The transfer reason is: {message}
    {warning}''').format(
        type=white('datasets' if item_type == IS_DATASET else 'reuses'),
        item_col=white(item_col),
        target_type=white('organizations' if target_type == ORG_TARGET else 'users'),
        target_col=white(target_col),
        source=white(file.name),
        message=message,
        total=white(len(rows)),
        warning=warning,
    ))
    if not force:
        click.confirm('Are you sure?', abort=True)
    click.echo('')

    # Perform
    total = 0
    item_endpoint = 'datasets/{id}/' if item_type == IS_DATASET else 'reuses/{id}/'
    item_type_label = 'dataset' if item_type == IS_DATASET else 'reuse'
    item_class = 'Dataset' if item_type == IS_DATASET else 'Reuse'
    target_endpoint = 'organizations/{id}/' if target_type == ORG_TARGET else 'users/{id}/'
    target_type_label = 'organization' if target_type == ORG_TARGET else 'user'
    target_class = 'Organization' if target_type == ORG_TARGET else 'User'
    target_fields = 'id,name' if target_type == ORG_TARGET else 'id,first_name,last_name'
    for line, row in enumerate(rows, 2):  # Line 1 is header
        item_id = row[item_col]
        item = api.get(item_endpoint.format(id=item_id),
                       fields='id,slug,title,owner,organization',
                       allow_failure=True)
        if hasattr(item, 'error_details'):
            log.warning('Error on line %s for %s %s: %s',
                        line, item_type_label, item_id, item.error_details)
            continue
        target_id = row[target_col]
        target = api.get(target_endpoint.format(id=target_id),
                         fields=target_fields,
                         allow_failure=True)
        if hasattr(target, 'error_details'):
            log.warning('Error on line %s for %s %s: %s',
                        line, target_type_label, target_id, target.error_details)
            continue
        if target_type == ORG_TARGET:
            target_name = target['name']
            if item.get('organization', {}).get('id') == target_id:
                log.info('Skipping %s %s (%s) as %s is already the owner',
                         item_type_label, item['title'], item['id'], target_name)
                continue
        else:
            target_name = '{first_name} {last_name}'.format(**target)
        log.info('Transfering %s %s (%s) to %s',
                 item_type_label, item['title'], item['id'], target_name)

        if dryrun:
            continue

        request_response = api.post('transfer/', {
            'comment': message,
            'recipient': {'class': target_class, 'id': target['id']},
            'subject': {'class': item_class, 'id': item['id']}
        })

        transfer_url = 'transfer/{id}/'.format(**request_response)
        accept_reponse = api.post(transfer_url, {
            'response': 'accept',
            'comment': 'Automatically accepted by udata-cli',
        }, allow_failure=True)

        if hasattr(accept_reponse, 'error_details'):
            log.warning('Unable to complete %s %s transfer to (%s) to %s: %s',
                        item_type_label, item['title'], item['id'],
                        target_name, accept_reponse.error_details)
        else:
            log.info('Transfered %s %s (%s) to %s',
                     item_type_label, item['title'], item['id'], target_name)
            total += 1

    success('Transfered {0} on {1} {2}(s)'.format(total, len(rows), item_type_label))
