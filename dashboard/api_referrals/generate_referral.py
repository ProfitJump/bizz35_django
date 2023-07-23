import secrets
import string


def new_referral_id():
    n = 8
    referral_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(n))

    return referral_id
