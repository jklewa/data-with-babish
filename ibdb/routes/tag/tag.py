from flask import jsonify, request, Blueprint, current_app

from ibdb.models import Tag

tag_bp = Blueprint('tag_bp', __name__, template_folder='templates')


@tag_bp.record
def record(state):
    db = state.app.config.get("db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through db")


@tag_bp.route('/tags')
def tags():
    q = Tag.query
    axis = request.args.get('axis')
    if axis:
        q = q.filter(Tag.axis == axis)
    rows = q.order_by(Tag.axis, Tag.name, Tag.id).all()
    return jsonify([t.serialize() for t in rows])


@tag_bp.route('/tag/<id>')
def tag_by(id):
    t = Tag.query.filter_by(id=id).first_or_404()
    return jsonify(t.serialize())


@tag_bp.route('/tag/<id>', methods=['POST'])
def tag_update(id):
    Tag.query.filter_by(id=id).update(request.form.to_dict())
    db = current_app.config['db']
    db.session.commit()
    updated = Tag.query.filter_by(id=id).first()
    return jsonify(updated.serialize())
