
from backend.services.auth.registration.validate_personal_information import validate_personal_information
from backend.services.auth.registration.send_email_otp import send_email_otp
from backend.services.auth.registration.confirm_email_otp import confirm_email_otp
from backend.services.auth.registration.complete_registration import complete_registration
from backend.services.auth.registration.confirm_password import confirm_password
from backend.services.auth.registration.validate_password import validate_password
from backend.services.auth.registration.cancel_registration import cancel_registration


class RegistrationServices:
    complete_registration = staticmethod(complete_registration)
    confirm_email_otp = staticmethod(confirm_email_otp)
    confirm_password = staticmethod(confirm_password)
    send_email_otp = staticmethod(send_email_otp)
    validate_personal_information = staticmethod(validate_personal_information)
    validate_password = staticmethod(validate_password)
    cancel_registration = staticmethod(cancel_registration)


registration_service = RegistrationServices()
