from flask import jsonify, request, Blueprint, current_app

base_bp = Blueprint('base_bp', __name__, template_folder='templates')


@base_bp.route('/')
def index():
    return jsonify({
        'description': 'Internet Babish DataBase (IBDB) API',
        'routes': sorted({
            f'{request.base_url[:-1]}{rule}'
            for rule in current_app.url_map.iter_rules()
            if not str(rule).startswith('/static')
        }),
    })
