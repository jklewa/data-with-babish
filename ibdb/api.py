import os

from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    render_template,
)

from models import (
    Episode,
    Recipe,
    Guest,
    Reference,
    t_episode_inspired_by,
    Show,
    db,
)

from utils import (
    normalize_raw_list
)

DB_USERNAME = os.environ.get('POSTGRES_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', 'db')
DB_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))

app = Flask(__name__, template_folder='/app/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/babish_db"
app.config['JSON_SORT_KEYS'] = False
db.init_app(app)


@app.route('/')
def index():
    return jsonify({
        'description': 'Internet Babish DataBase (IBDB) API',
        'routes': sorted(
            set(
                f'{request.base_url[:-1]}{rule}'
                for rule in app.url_map.iter_rules()
            )
        )[:-1],
    })


@app.route('/episodes')
def episodes():
    episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([e.serialize() for e in episodes])
    else:
        references = Reference.query.order_by(Reference.name, Reference.id).all()
        shows = Show.query.order_by(Show.id).all()
        return render_template('episodes.html', episodes=episodes, references=references, shows=shows)


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
    return redirect('/episodes#' + str(new.id))


@app.route('/episode/<id>', methods=['GET'])
def episode_by(id):
    ep = Episode.query.filter_by(id=id).first_or_404()
    return jsonify(ep.serialize())


@app.route('/episode/<id>', methods=['POST'])
def episode_update(id):
    Episode.query.filter_by(id=id).update(request.form.to_dict())
    db.session.commit()
    redirect('/episodes#' + str(id))


@app.route('/episode/<id>/inspired_by', methods=['POST'])
def episode_inspired_by(id):
    ep = Episode.query.get(id)
    ref = Reference.query.get(request.form.get("inspiration_reference_id"))
    ep.inspired_by.append(ref)
    db.session.add(ep)
    db.session.commit()
    return redirect('/episodes#' + str(ep.id))


@app.route('/recipes')
def recipes():
    recipes = Recipe.query.order_by(Recipe.name, Recipe.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in recipes])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('recipes.html', recipes=recipes, episodes=episodes)


@app.route('/recipes', methods=['POST'])
def recipe_new():
    new = Recipe(
        name=request.form.get("name"),
        image_link=request.form.get("image_link"),
        raw_ingredient_list=normalize_raw_list(
            request.form.get("raw_ingredient_list")),
        raw_procedure=normalize_raw_list(
            request.form.get("raw_procedure")),
        episode_id=request.form.get("source_episode_id"),
    )
    db.session.add(new)
    db.session.commit()
    return redirect('/recipes#r' + str(new.id))


@app.route('/recipe/<id>')
def recipe_by(id):
    r = Recipe.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@app.route('/recipe/<id>', methods=['POST'])
def recipe_update(id):
    Recipe.query.filter_by(id=id).update(request.form.to_dict())
    db.session.commit()
    return redirect('/recipes#r' + str(id))


@app.route('/guests')
def guests():
    guests = Guest.query.order_by(Guest.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([g.serialize() for g in guests])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('guests.html', guests=guests, episodes=episodes)


@app.route('/guests', methods=['POST'])
def guest_new():
    new = Guest(
        name=request.form.get("name"),
        image_link=request.form.get("image_link"),
    )
    appearance = Episode.query.get(
        request.form.get("appearance_episode_id")
    )
    if appearance:
        new.appearances.append(appearance)
    db.session.add(new)
    db.session.commit()
    return redirect('/guests#g' + str(new.id))


@app.route('/guest/<id>/appearances', methods=['POST'])
def guest_appearances(id):
    guest = Guest.query.get(id)
    appearance = Episode.query.get(request.form.get("appearance_episode_id"))
    guest.appearances.append(appearance)
    db.session.add(guest)
    db.session.commit()
    return redirect('/guests#g' + str(guest.id))


@app.route('/guest/<id>')
def guest_by(id):
    g = Guest.query.filter_by(id=id).first_or_404()
    return jsonify(g.serialize())


@app.route('/guest/<id>', methods=['POST'])
def guest_update(id):
    Guest.query.filter_by(id=id).update(request.form.to_dict())
    db.session.commit()
    return redirect('/guests#g' + str(id))


@app.route('/references')
def references():
    references = Reference.query.order_by(Reference.name, Reference.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in references])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('references.html', references=references, episodes=episodes)


@app.route('/references', methods=['POST'])
def reference_new():
    new = Reference(
        type=request.form.get("type"),
        name=request.form.get("name"),
        image_link=request.form.get("image_link"),
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
    return redirect('/references#r' + str(new.id))


@app.route('/reference/<id>/episodes_inspired', methods=['POST'])
def reference_episodes_inspired(id):
    ref = Reference.query.get(id)
    inspired = Episode.query.get(request.form.get("inspired_episode_id"))
    ref.episodes_inspired.append(inspired)
    db.session.add(ref)
    db.session.commit()
    return redirect('/references#r' + str(ref.id))


@app.route('/reference/<id>')
def reference_by(id):
    r = Reference.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@app.route('/reference/<id>', methods=['POST'])
def reference_update(id):
    Reference.query.filter_by(id=id).update(request.form.to_dict())
    db.session.commit()
    return redirect('/references#r' + str(id))


@app.route('/shows')
def shows():
    shows = Show.query.order_by(Show.id).all()
    return jsonify([s.serialize() for s in shows])


@app.route('/show/<id>')
def show_by(id):
    s = Show.query.filter_by(id=id).first_or_404()
    return jsonify(s.serialize())


@app.route('/show/<id>', methods=['POST'])
def show_update(id):
    Show.query.filter_by(id=id).update(request.form.to_dict())
    db.session.commit()
    updated = Show.query.filter_by(id=id).first()
    return jsonify(updated.serialize())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
