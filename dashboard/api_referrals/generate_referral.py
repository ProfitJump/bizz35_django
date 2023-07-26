import string
import secrets

def new_referral_id():
    n = 8
    characters = string.ascii_uppercase + string.digits

    # Remove confusing characters from the pool of choices
    for char in 'IL10Oo':
        characters = characters.replace(char, '')

    referral_id = ''.join(secrets.choice(characters) for i in range(n))

    # If the generated ID is not 8 characters long, pad it with additional characters
    if len(referral_id) < n:
        padding = secrets.choice(string.ascii_uppercase + string.digits)
        referral_id += padding * (n - len(referral_id))

    return referral_id

new_id = new_referral_id()
print("Generated ID:", new_id)
