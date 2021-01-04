from flask import current_app, Blueprint, jsonify, request, redirect, render_template

from ibdb.models import Episode, Reference, Show

episode_bp = Blueprint('episode_bp', __name__, template_folder='templates')


@episode_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@episode_bp.route('/episodes')
def episodes():
    episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
    if request.args.get('format', None) == 'json':
        return jsonify([e.serialize() for e in episodes])
    else:
        references = Reference.query.order_by(Reference.name, Reference.id).all()
        shows = Show.query.order_by(Show.id).all()
        return render_template('episode/list_edit.html', episodes=episodes, references=references, shows=shows)


@episode_bp.route('/episodes', methods=['POST'])
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
    db = current_app.config['db']
    db.session.add(new)
    db.session.commit()
    return redirect('/episodes#' + str(new.id))


@episode_bp.route('/episode/<id>', methods=['GET'])
def episode_by(id):
    ep = Episode.query.filter_by(id=id).first_or_404()
    return jsonify(ep.serialize())


@episode_bp.route('/episode/<id>', methods=['POST'])
def episode_update(id):
    Episode.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    redirect('/episodes#' + str(id))


@episode_bp.route('/episode/<id>/inspired_by', methods=['POST'])
def episode_inspired_by(id):
    ep = Episode.query.get(id)
    ref = Reference.query.get(request.form.get("inspiration_reference_id"))
    ep.inspired_by.append(ref)
    db = current_app.config['db']
    db.session.add(ep)
    db.session.commit()
    return redirect('/episodes#' + str(ep.id))
