import os

import click

from ibdb.api import app
from ibdb.export import export as sync_export


@app.cli.command('api')
def api():
    app.run(debug=True, host='0.0.0.0')


@app.cli.group('sync', chain=True)
def sync():
    pass


@sync.command('export')
@click.option('--format', '-f', multiple=True, default=["json", "sql"], type=click.Choice(['json', 'sql']),
              help='Output formats (default: json,sql)')
def export(format):
    sync_export(json_='json' in format, sql='sql' in format)


def main():
    os.environ['FLASK_APP'] = 'ibdb.api'
    return app.cli.main()
