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

app = Flask(__name__, template_folder='/app/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres@db:5432/babish_db"
db.init_app(app)


@app.route('/')
def index():
    return jsonify({
        'description': 'Internet Babish DataBase (IBDB) API',
        'routes': sorted([f'{request.base_url[:-1]}{rule}' for rule in app.url_map.iter_rules()])[:-1],
    })


@app.route('/episodes')
def episodes():
    episodes = Episode.query.order_by(Episode.published_date.desc()).all()
    if request.args.get('format', None) == 'json':
        return jsonify([e.serialize() for e in episodes])
    else:
        references = Reference.query.order_by(Reference.name).all()
        return render_template('episodes.html', episodes=episodes, references=references)


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


@app.route('/episode/<id>/inspired_by', methods=['POST'])
def episode_inspired_by(id):
    ep = Episode.query.get(id)
    ref = Reference.query.get(request.form.get("inspiration_reference_id"))
    ep.inspired_by.append(ref)
    db.session.add(ep)
    db.session.commit()
    return redirect('/episodes#' + str(ep.id))


@app.route('/episode/<id>')
def episode_by(id):
    ep = Episode.query.filter_by(id=id).first_or_404()
    return jsonify(ep.serialize())


@app.route('/recipes')
def recipes():
    recipes = Recipe.query.order_by(Recipe.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in recipes])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc()).all()
        return render_template('recipes.html', recipes=recipes, episodes=episodes)


@app.route('/recipes', methods=['POST'])
def recipe_new():
    new = Recipe(
        name=request.form.get("name"),
        raw_ingredient_list=request.form.get("raw_ingredient_list"),
        raw_procedure=request.form.get("raw_procedure"),
        episode_id=request.form.get("source_episode_id"),
    )
    db.session.add(new)
    db.session.commit()
    return redirect('/recipes#' + str(new.id))


@app.route('/recipe/<id>')
def recipe_by(id):
    r = Recipe.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@app.route('/guests')
def guests():
    guests = Guest.query.order_by(Guest.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([g.serialize() for g in guests])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc()).all()
        return render_template('guests.html', guests=guests, episodes=episodes)


@app.route('/guests', methods=['POST'])
def guest_new():
    new = Guest(
        name=request.form.get("name"),
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


@app.route('/references')
def references():
    references = Reference.query.order_by(Reference.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in references])
    else:
        episodes = Episode.query.outerjoin(t_episode_inspired_by).order_by(
            Episode.show_id,
            t_episode_inspired_by.c.reference_id.nullsfirst(),
            Episode.published_date.desc(),
        ).all()
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
    return redirect('/references')
    # return redirect('/references#r' + str(new.id))


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
