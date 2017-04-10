# udata-cli

A uData API console client for common administrative tasks.

This tools is not meant to be mainstream.
It only provides a udata API usage example and a framework to perform
some administrative tasks.


## Requirements

`udata-cli` requires Python 3 and until the Python Click 7.0
is released, it requires the development version.

## Installation

In a `virtualenv`

```shell
pip install https://github.com/pallets/click/tarball/master
pip install https://github.com/opendatateam/udata-cli/tarball/master
```

## Usage

```shell
ucli --help
```

`ucli` needs to know which udata instance to use and for authenticated operations
it also requires an API token.

You can provide both with the dedicated parameters:

```shell
ucli --url https://udata.somedomain.org --token xyz123 operation
```

or exposing the right environment variables:

```shell
export UDATA_URL='https://udata.somedomain.org'
export UDATA_TOKEN='xyz123'
ucli operation
```

**Important**: This tool is provided as it is.
Even if contributions are open, there won't be any dedicated support.
