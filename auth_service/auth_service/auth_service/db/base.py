# Import all the models, so that Base has them before being
# imported by Alembic


from auth_service.db.session import Base  # noqa
from auth_service.models import *  # noqa
