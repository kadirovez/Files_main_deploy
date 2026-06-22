
from backend.crud.auth.base import CRUDSessionBase
from backend.models.auth.main import Main
from backend.schemas.auth.main import MainCreate, MainUpdate


class CRUDMain(CRUDSessionBase[Main, MainCreate, MainUpdate]):
    ''' CRUD operations for main sessions '''


main_crud = CRUDMain(Main)