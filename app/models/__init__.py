# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.model_base import Base  # noqa
from app.models.model_history import History
from app.models.model_patient import Patient
from app.models.model_clinic import Clinic
from app.models.model_clinic_history import ClinicHistory
