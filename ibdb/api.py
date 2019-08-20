from flask import (
    Flask,
    jsonify,
    request,
)

from models import (
    Episode,
    Recipe,
    Guest,
    Reference,
    db,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres@db:5432/babish_db"
db.init_app(app)


@app.route('/')
def index():
    return jsonify({
        'description': 'Internet Babish DataBase (IBDB) API',
        'routes': sorted([f'{request.base_url[:-1]}{rule}' for rule in app.url_map.iter_rules()][:-1])
    })


@app.route('/episodes')
def episodes():
    episodes = Episode.query.all()
    return jsonify([e.serialize() for e in episodes])


@app.route('/recipes')
def recipes():
    recipes = Recipe.query.all()
    return jsonify([r.serialize() for r in recipes])


@app.route('/guests')
def guests():
    guests = Guest.query.all()
    return jsonify([g.serialize() for g in guests])


@app.route('/references')
def references():
    references = Reference.query.all()
    return jsonify([r.serialize() for r in references])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
