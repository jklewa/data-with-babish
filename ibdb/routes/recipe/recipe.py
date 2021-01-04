from flask import jsonify, request, render_template, redirect, Blueprint, current_app

from ibdb.models import Recipe, Episode
from ibdb.utils import normalize_raw_list

recipe_bp = Blueprint('recipe_bp', __name__, template_folder='templates')


@recipe_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@recipe_bp.route('/recipes')
def recipes():
    recipes = Recipe.query.order_by(Recipe.name, Recipe.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in recipes])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('recipe/list_edit.html', recipes=recipes, episodes=episodes)


@recipe_bp.route('/recipes', methods=['POST'])
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
    db = current_app.config['db']
    db.session.add(new)
    db.session.commit()
    return redirect('/recipes#r' + str(new.id))


@recipe_bp.route('/recipe/<id>')
def recipe_by(id):
    r = Recipe.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@recipe_bp.route('/recipe/<id>', methods=['POST'])
def recipe_update(id):
    Recipe.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    return redirect('/recipes#r' + str(id))
