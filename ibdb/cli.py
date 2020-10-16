import os

import click
from ibdb.api import app

@app.cli.command('test')
@click.argument('foo')
def test(foo):
    print(foo)

def main():
    os.environ['FLASK_APP'] = 'ibdb.api'
    return app.cli.main()