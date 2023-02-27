# Import all the models, so that Base has them before being
# imported by Alembic


from order_service.db.session import Base  # noqa
from order_service.models import *  # noqa
