from .base.base import base_bp
from .episode.episode import episode_bp
from .guest.guest import guest_bp
from .recipe.recipe import recipe_bp
from .reference.reference import reference_bp
from .show.show import show_bp

blueprints = [
    base_bp,
    episode_bp,
    guest_bp,
    recipe_bp,
    reference_bp,
    show_bp,
]
