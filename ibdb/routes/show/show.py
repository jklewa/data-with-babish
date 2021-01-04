from flask import jsonify, request, Blueprint, current_app

from ibdb.models import Show

show_bp = Blueprint('show_bp', __name__, template_folder='templates')


@show_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@show_bp.route('/shows')
def shows():
    shows = Show.query.order_by(Show.id).all()
    return jsonify([s.serialize() for s in shows])


@show_bp.route('/show/<id>')
def show_by(id):
    s = Show.query.filter_by(id=id).first_or_404()
    return jsonify(s.serialize())


@show_bp.route('/show/<id>', methods=['POST'])
def show_update(id):
    Show.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    updated = Show.query.filter_by(id=id).first()
    return jsonify(updated.serialize())
