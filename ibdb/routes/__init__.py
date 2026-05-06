from .base.base import base_bp
from .episode.episode import episode_bp
from .guest.guest import guest_bp
from .recipe.recipe import recipe_bp
from .reference.reference import reference_bp
from .tag.tag import tag_bp

blueprints = [
    base_bp,
    episode_bp,
    guest_bp,
    recipe_bp,
    reference_bp,
    tag_bp,
]
