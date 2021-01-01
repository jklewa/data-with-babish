import os

from ibdb.api import app
from ibdb.populate_db import main as populate_db_main
from ibdb.sync import export as sync_export


@app.cli.command('run')
def run():
    app.run(debug=True, host='0.0.0.0')


@app.cli.group('sync', chain=True)
def sync():
    pass


@sync.command('update')
def update():
    populate_db_main()


@sync.command('export')
def export():
    sync_export()


def main():
    os.environ['FLASK_APP'] = 'ibdb.api'
    return app.cli.main()
