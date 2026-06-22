
from backend.services.auth.login.cancel_login import cancel_login
from backend.services.auth.login.complete_login import complete_login
from backend.services.auth.login.confirm_email import confirm_email
from backend.services.auth.login.confirm_email_otp import confirm_email_otp
from backend.services.auth.login.send_email_otp import send_email_otp
from backend.services.auth.login.validate_email import validate_email
from backend.services.auth.login.validate_identifier import validate_identifier
from backend.services.auth.login.validate_password import validate_password
from backend.services.auth.login.validate_username import validate_username


class LoginServices:
    validate_username = staticmethod(validate_username)
    validate_email = staticmethod(validate_email)
    validate_identifier = staticmethod(validate_identifier)
    validate_password = staticmethod(validate_password)
    confirm_email = staticmethod(confirm_email)
    send_email_otp = staticmethod(send_email_otp)
    confirm_email_otp = staticmethod(confirm_email_otp)
    complete_login = staticmethod(complete_login)
    cancel_login = staticmethod(cancel_login)


login_service = LoginServices()
