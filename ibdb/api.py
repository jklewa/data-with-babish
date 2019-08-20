from flask import (
    Flask,
    jsonify,
    request,
    render_template,
)

from models import (
    Episode,
    Recipe,
    Guest,
    Reference,
    Show,
    db,
)

app = Flask(__name__, template_folder='/app/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres@db:5432/babish_db"
db.init_app(app)


@app.route('/')
def index():
    return jsonify({
        'description': 'Internet Babish DataBase (IBDB) API',
        'routes': sorted([f'{request.base_url[:-1]}{rule}' for rule in app.url_map.iter_rules()])[:-1]
    })


@app.route('/episodes')
def episodes():
    episodes = Episode.query.order_by(Episode.published_date.desc()).all()
    if request.args.get('format', None) == 'json':
        return jsonify([e.serialize() for e in episodes])
    else:
        return render_template('episodes.html', episodes=episodes)


@app.route('/episodes', methods=['POST'])
def episode_new():
    new = Episode(
        id=request.form.get("episode_id"),
        name=request.form.get("name"),
        youtube_link=request.form.get("youtube_link"),
        official_link=request.form.get("official_link"),
        image_link=request.form.get("image_link"),
        published_date=request.form.get("published_date"),
        show_id=request.form.get("show_id"),
    )
    db.session.add(new)
    db.session.commit()
    return jsonify(new.serialize())


@app.route('/episode/<id>')
def episode_by(id):
    ep = Episode.query.filter_by(id=id).first_or_404()
    return jsonify(ep.serialize())


@app.route('/recipes')
def recipes():
    recipes = Recipe.query.order_by(Recipe.name).all()
    return jsonify([r.serialize() for r in recipes])


@app.route('/recipes', methods=['POST'])
def recipe_new():
    new = Recipe(
        name=request.form.get("name"),
        raw_ingredient_list=request.form.get("raw_ingredient_list"),
        raw_procedure=request.form.get("raw_procedure"),
        episode_id=request.form.get("episode_id"),
    )
    db.session.add(new)
    db.session.commit()
    return jsonify(new.serialize())


@app.route('/recipe/<id>')
def recipe_by(id):
    r = Recipe.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@app.route('/guests')
def guests():
    guests = Guest.query.order_by(Guest.name).all()
    return jsonify([g.serialize() for g in guests])


@app.route('/guests', methods=['POST'])
def guest_new():
    new = Guest(
        name=request.form.get("name"),
    )
    db.session.add(new)
    db.session.commit()
    return jsonify(new.serialize())


@app.route('/guest/<id>')
def guest_by(id):
    g = Guest.query.filter_by(id=id).first_or_404()
    return jsonify(g.serialize())


@app.route('/references')
def references():
    references = Reference.query.order_by(Reference.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in references])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc()).all()
        return render_template('references.html', references=references, episodes=episodes)


@app.route('/references', methods=['POST'])
def reference_new():
    new = Reference(
        type=request.form.get("type"),
        name=request.form.get("name"),
        description=request.form.get("description"),
        external_link=request.form.get("external_link"),
    )
    inspired = Episode.query.get(
        request.form.get("inspired_episode_id")
    )
    if inspired:
        new.episodes_inspired.append(inspired)
    db.session.add(new)
    db.session.commit()
    return jsonify(new.serialize())


@app.route('/reference/<id>')
def reference_by(id):
    r = Reference.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@app.route('/shows')
def shows():
    shows = Show.query.order_by(Show.id).all()
    return jsonify([s.serialize() for s in shows])


@app.route('/show/<id>')
def show_by(id):
    s = Show.query.filter_by(id=id).first_or_404()
    return jsonify(s.serialize())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
