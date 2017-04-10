import csv
import logging
import sys

from textwrap import dedent

import click

from ucli import suggest
from ucli.api import pass_api
from ucli.utils import header, prompt_choices, choice_enum, label_arrow, white, success

from . import datasets

log = logging.getLogger(__name__)


@datasets.command()
@click.argument('csvfile', type=click.File('r'))
                # help='The CSV file containing identifiers to remove')
@click.option('--column', type=str, default='id',
                help='The name of the column containing identifiers to remove')
@pass_api
def delete(api, csvfile, column):
    '''Massive datasets deletion from a CSV file'''
    header(delete.__doc__)

    data = csv.DictReader(csvfile)
    deleted = 0

    for row in data:
        id = row[column]
        response = api.delete('datasets/{id}/'.format(id=id), allow_failure=True)
        if response.status_code == 204:
            deleted += 1
            log.info('Deleted dataset %s', id)
        elif response.status_code == 410:
            log.info('Dataset %s is already deleted', id)
        elif response.status_code == 404:
            log.warning('Dataset %s does not exists', id)
        else:
            log.error('Unable to delete delete dataset %s: %s (%s)', id, response.reason, response.status_code,
                      extra={'details': getattr(response, 'error_details', None)})

    success('Deleted {0} dataset(s)'.format(deleted))
