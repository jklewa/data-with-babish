import os

from ibdb.api import app
from ibdb.populate_db import main as populate_db_main
from ibdb.sync import main as sync_main


@app.cli.command('run')
def run():
    app.run(debug=True, host='0.0.0.0')


@app.cli.command('sync')
def sync():
    populate_db_main()
    sync_main()


def main():
    os.environ['FLASK_APP'] = 'ibdb.api'
    return app.cli.main()
