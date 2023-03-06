# Import all the models, so that Base has them before being
# imported by Alembic


from employee_service.db.session import Base  # noqa
from employee_service.models import *  # noqa
