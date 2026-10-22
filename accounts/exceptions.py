from rest_framework.exceptions import APIException


class DuplicateAddressError(APIException):
    status_code = 409
    default_detail = "This address already exists."
    default_code = "duplicate_addresses"


class InvalidPasswordResetError(APIException):
    status_code = 400
    default_detail = "Invalid or expired reset token."
    default_code = "invalid_reset_token"
    