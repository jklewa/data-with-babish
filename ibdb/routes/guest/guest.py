from flask import jsonify, request, render_template, redirect, Blueprint, current_app

from ibdb.models import Guest, Episode

guest_bp = Blueprint('guest_bp', __name__, template_folder='templates')


@guest_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@guest_bp.route('/guests')
def guests():
    guests = Guest.query.order_by(Guest.name).all()
    if request.args.get('format', None) == 'json':
        return jsonify([g.serialize() for g in guests])
    else:
        episodes = Episode.query.order_by(Episode.published_date.desc(), Episode.id).all()
        return render_template('guest/list_edit.html', guests=guests, episodes=episodes)


@guest_bp.route('/guests', methods=['POST'])
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
    db = current_app.config['db']
    db.session.add(new)
    db.session.commit()
    return redirect('/guests#g' + str(new.id))


@guest_bp.route('/guest/<id>/appearances', methods=['POST'])
def guest_appearances(id):
    guest = Guest.query.get(id)
    appearance = Episode.query.get(request.form.get("appearance_episode_id"))
    guest.appearances.append(appearance)
    db = current_app.config['db']
    db.session.add(guest)
    db.session.commit()
    return redirect('/guests#g' + str(guest.id))


@guest_bp.route('/guest/<id>')
def guest_by(id):
    g = Guest.query.filter_by(id=id).first_or_404()
    return jsonify(g.serialize())


@guest_bp.route('/guest/<id>', methods=['POST'])
def guest_update(id):
    Guest.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    return redirect('/guests#g' + str(id))