from flask import jsonify, request, render_template, redirect, current_app, Blueprint

from ibdb.models import Reference, Episode

reference_bp = Blueprint('reference_bp', __name__, template_folder='templates')


@reference_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@reference_bp.route('/references')
def references():
    references = Reference.query.order_by(Reference.name, Reference.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([r.serialize() for r in references])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('reference/list_edit.html', references=references, episodes=episodes)


@reference_bp.route('/references', methods=['POST'])
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
    db = current_app.config['db']
    db.session.add(new)
    db.session.commit()
    return redirect('/references#r' + str(new.id))


@reference_bp.route('/reference/<id>/episodes_inspired', methods=['POST'])
def reference_episodes_inspired(id):
    ref = Reference.query.get(id)
    inspired = Episode.query.get(request.form.get("inspired_episode_id"))
    ref.episodes_inspired.append(inspired)
    db = current_app.config['db']
    db.session.add(ref)
    db.session.commit()
    return redirect('/references#r' + str(ref.id))


@reference_bp.route('/reference/<id>')
def reference_by(id):
    r = Reference.query.filter_by(id=id).first_or_404()
    return jsonify(r.serialize())


@reference_bp.route('/reference/<id>', methods=['POST'])
def reference_update(id):
    Reference.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    return redirect('/references#r' + str(id))