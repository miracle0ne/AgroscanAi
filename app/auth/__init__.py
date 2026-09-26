from flask_login import current_user
from app.extensions import login_manager
from app.models.users import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
