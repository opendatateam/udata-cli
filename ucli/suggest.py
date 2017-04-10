import click

from .utils import prompt_choices


DEFAULT_SIZE = 10


def suggest(prompt, api, endpoint, display, size=DEFAULT_SIZE):
    choice = 'r'
    while choice == 'r':
        q = click.prompt(prompt)
        results = api.get(endpoint, q=q, size=size)
        choices = list(enumerate((display(r) for r in results), 1))
        choices.append(('r', 'Retry'))
        choice = prompt_choices('Which one ?', *choices)
    index = int(choice) - 1
    return results[index]


def users(api):
    user = suggest(
        'Enter a query to find an user (ID, name...)',
        api, 'users/suggest/',
        lambda u: ' '.join((u['first_name'], u['last_name']))
    )
    return user


def organizations(api):
    organization = suggest(
        'Enter a query to find an organization (ID, name...)',
        api, 'organizations/suggest/',
        lambda o: o['name']
    )
    return organization


def datasets(api):
    dataset = suggest(
        'Enter a query to find a dataset (ID, title...)',
        api, 'datasets/suggest/',
        lambda d: d['title']
    )
    return dataset


def reuses(api):
    reuse = suggest(
        'Enter a query to find a reuse (ID, title...)',
        api, 'reuses/suggest/',
        lambda r: r['title']
    )
    return reuse


def territory(api):
    pass
