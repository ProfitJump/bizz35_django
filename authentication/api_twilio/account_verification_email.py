# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid, auth_token)


def two_step_email(email, name, session_email):
    verification = client.verify \
        .v2 \
        .services(os.getenv("SERVICE")) \
        .verifications \
        .create(channel_configuration={
            'substitutions': {
                'firstname': name,
                'email': session_email
                },
            'template_id': os.getenv("TEMPLATE"),
            'from': 'support@bizz35.com',
            'from_name': 'Bizz35 Support'
            },
            to=email, channel='email'
        )

    # print(verification.sid)
    # print(verification.service_sid)
    # print(verification.account_sid)
    # print(verification.to)
    # print(verification.channel)
    # print(verification.status)
    # print(verification.valid)
    # print(verification.amount)
    # print(verification.payee)
    # print(verification.send_code_attempts)
    # print(verification.date_created)
    # print(verification.date_updated)


def two_step_email_response(email, code):
    verification_check = client.verify \
        .v2 \
        .services(os.getenv("SERVICE")) \
        .verification_checks \
        .create(to=email, code=code)

    # print(verification_check.sid)
    # print(verification_check.status)
    return verification_check.status
