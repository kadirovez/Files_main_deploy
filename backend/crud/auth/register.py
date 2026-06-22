
from backend.crud.auth.base import CRUDSessionBase
from backend.models.auth.register_session import Registration
from backend.schemas.auth.base import CreateSessionSchema
from backend.schemas.auth.registration import RegistrationUpdate


class CRUDRegistration(CRUDSessionBase[Registration, CreateSessionSchema, RegistrationUpdate]):
    ''' CRUD operations for registration session '''

    reset_values = {
        "username": None,
        "first_name": None,
        "last_name": None,
        "email": None,
        "password": None,
        "password_is_confirmed": False,
        "email_is_confirmed": False,
        "email_code_sent": None,
        "email_code_id": None,
        "email_code_expire_at": None,
        "is_completed": False,
    }


registration_crud = CRUDRegistration(Registration)

