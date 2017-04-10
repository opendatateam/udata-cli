import logging

import click

from .utils import color, yellow, red, cyan, white, ARROW, MAGNIFYING_GLASS


LEVEL_COLORS = {
    logging.WARNING: yellow,
    logging.ERROR: red,
    logging.CRITICAL: color('black', bg='red', bold=True),
}


class CliFormatter(logging.Formatter):
    '''
    Convert a `logging.LogRecord' object into colored text,
    using ANSI escape sequences.
    '''
    def format(self, record):
        msg = record.getMessage()

        if record.levelno == logging.INFO:
            return ' '.join((cyan(ARROW), msg))
        if record.levelno == logging.DEBUG:
            return ' '.join((cyan(MAGNIFYING_GLASS), msg))
        else:
            color = LEVEL_COLORS.get(record.levelno, white)
            return ': '.join((color(record.levelname.lower()), msg))


class CliHandler(logging.Handler):
    '''
    Log using ``click.echo``
    Support an optionnal ``record.details`` attribute.
    '''
    def emit(self, record):
        try:
            msg = self.format(record)
            err = record.levelno >= logging.WARNING
            click.echo(msg, err=err)
            details = getattr(record, 'details', None)
            if details:
                click.echo(details)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def init_logging(verbose=False):
    logger = logging.getLogger()
    handler = CliHandler()
    handler.setFormatter(CliFormatter())
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
