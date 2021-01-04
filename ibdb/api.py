import os
from flask import Flask
from flask_migrate import Migrate

from ibdb.models import db
from ibdb.routes import blueprints

app = Flask(__name__, template_folder='./templates')
app.config.from_object(os.environ.get('APP_SETTINGS', 'ibdb.settings.FlaskConfig'))
app.config['db'] = db
db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)

for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
