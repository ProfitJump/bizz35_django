from django.core.management.base import BaseCommand
from django.db.models import Sum
from datetime import datetime, timedelta
from dashboard.models import LedgerEntry
from authentication.models import User
import time


class Command(BaseCommand):
    help = 'Checks whether a shipment of SportsPro is due for all users'

    def handle(self, *args, **options):
        while True:
            # Get all users
            users = User.objects.all()

            for user in users:
                # Retrieve ledger entries for the current user and SportsPro ledger, sorted by timestamp
                user_ledger = LedgerEntry.objects.filter(user=user, ledger_name='SportsPro').order_by('timestamp')

                # Check if there are any ledger entries for the user
                if not user_ledger:
                    continue

                # Calculate the user's balance based on the ledger entries
                user_balance = user_ledger.aggregate(balance=Sum('debit') - Sum('credit'))['balance']

                # Check if user_balance is not None and is greater than or equal to 74
                if user_balance is not None and user_balance >= 74:
                    # Check if one month has passed since last shipment
                    last_shipment = user_ledger.filter(credit=15.50).last()
                    if last_shipment:
                        time_since_shipment = datetime.now().date() - last_shipment.timestamp.date()
                        print(time_since_shipment)
                        days_till_shipment = timedelta(days=30) - time_since_shipment
                        if time_since_shipment >= timedelta(minutes=30):
                            # Create a new LedgerEntry with a credit of 15.50
                            LedgerEntry.objects.create(user=user, description='SportsPro Shipment Completed', ledger_name='SportsPro', credit=15.50, debit=0, is_public=True)
                            LedgerEntry.objects.create(user=user, description='WildAspen Balance Transfer', ledger_name='SportsPro', credit=50.00, debit=0, is_public=True)
                            LedgerEntry.objects.create(user=user, description='SportsPro Balance Transfer', ledger_name='WildAspen', credit=0, debit=50.00, is_public=True)
                            LedgerEntry.objects.create(user=user, description='eWallet Balance Transfer', ledger_name='SportsPro', credit=8.50, debit=0, is_public=True)
                            LedgerEntry.objects.create(user=user, description='SportsPro Balance Transfer', ledger_name='eWallet', credit=0, debit=8.50, is_public=True)
                            self.stdout.write(self.style.SUCCESS('SportsPro Shipment made for user {}. Days till next shipment: {}'.format(user.username, days_till_shipment.days)))
                        else:
                            self.stdout.write(self.style.SUCCESS('SportsPro Shipment not due for user {}. Days till next shipment: {}'.format(user.username, days_till_shipment.days)))
                    else:
                        # Create a new LedgerEntry with a credit of 15.50
                        LedgerEntry.objects.create(user=user, description='SportsPro Shipment Completed', ledger_name='SportsPro', credit=15.50, debit=0, is_public=True)
                        LedgerEntry.objects.create(user=user, description='WildAspen Balance Transfer', ledger_name='SportsPro', credit=50.00, debit=0, is_public=True)
                        LedgerEntry.objects.create(user=user, description='SportsPro Balance Transfer', ledger_name='WildAspen', credit=0, debit=50.00, is_public=True)
                        LedgerEntry.objects.create(user=user, description='eWallet Balance Transfer', ledger_name='SportsPro', credit=8.50, debit=0, is_public=True)
                        LedgerEntry.objects.create(user=user, description='SportsPro Balance Transfer', ledger_name='eWallet', credit=0, debit=8.50, is_public=True)
                        self.stdout.write(self.style.SUCCESS('SportsPro Shipment made for user {}. Days till next shipment: {}'.format(user.username, 30)))
                else:
                    self.stdout.write(self.style.SUCCESS('SportsPro Shipment not due for user {}'.format(user.username)))

            # Count down till the next check
            self.stdout.write('\n')
            self.stdout.write(self.style.SUCCESS('Waiting for next check in:'))
            for i in range(120, 0, -1):
                m, s = divmod(i, 60)
                h, m = divmod(m, 60)
                time_left = "{:02d}:{:02d}:{:02d}".format(h, m, s)
                self.stdout.write(self.style.SUCCESS(time_left), ending='\r')
                time.sleep(1)
            self.stdout.write('\n')  # Print newline to avoid overlapping with the next check's output
