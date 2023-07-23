import time

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from dashboard.models import Profile, BoosterNumbers, BoosterProfile
from django.contrib.auth import get_user_model
from dashboard.views import add_ledger_entry


class Command(BaseCommand):
    help = 'This command is used to start the automation of assigning out boosters in the matrix.'

    def handle(self, *args, **options):
        # Pass a dummy request object to make the ledgers work.
        request = None
        # Keep running until the system is restarted, or the command is stopped. Makes sure to stop and start this command when updating the code.
        # the loop runs every 1 second, based on the wait command at the end.
        while True:
            # The system will go and look for all user accounts that have a True flag set to a field called is_booster in the Profiles model.
            # if this flag is true it will then add them to a model called BoosterProfile to be assigned out to a user. The booster must be
            # a paid member to be eligible to be assigned out.
            users = get_user_model().objects.filter(profile__is_booster=True).exclude(profile__membership_level='Free User')
            boosters = [booster.user for booster in BoosterProfile.objects.all()]
            for user in users:
                if user not in boosters:
                    booster = BoosterProfile(user=user)
                    booster.save()
            # The system looks to see if the True flag has been removed from the is_booster field. If it has the system will remove them from
            # the BoosterProfile model. This stops the booster from being assigned to multiple people.
            for booster in boosters:
                if not booster.profile.is_booster:
                    BoosterProfile.objects.filter(user=booster).delete()

            # The system then goes and looks for all accounts that have a value > 0 in a field called boosters in the Profile model.
            profiles = Profile.objects.filter(boosters__gt=0)
            if not profiles:
                # If no users have a booster to use up then they system will go out and get a random profile and add 1 to the boosters count.
                # If the user is not a paying member or have not signed up 3 members, they are not eligible to get a booster assigned to them.
                random_profile = Profile.objects.exclude(membership_level='Free User').exclude(matrix_level__lt=3).order_by('?').first()
                if random_profile:
                    random_profile.boosters += 1
                    random_profile.save()
                    booster_number, created = BoosterNumbers.objects.get_or_create(user=random_profile.user)
                    booster_number.count = random_profile.boosters
                    booster_number.save()
                else:
                    # Keep passing until there are users in the system.
                    print('There are currently no user accounts to assign boosters too.')
            else:
                # Here the system has found a profile with a booster count > 0. The system then add them to a model called BoosterNumbers.
                # If the count is updated, e.g. they get more boosters it updates the count, but they do not lose their place in line. The timestamp
                # is only updated when they are first added to the BoostersNumbers model. If a user buys or get's assigned boosters mid-cycle
                # then they are first in line at the start of the next cycle.
                for profile in profiles:
                    user = profile.user
                    booster_number, created = BoosterNumbers.objects.get_or_create(user=user)
                    booster_number.count = profile.boosters
                    if booster_number.count > profile.boosters:
                        booster_number.timestamp = timezone.now() - timedelta(seconds=1)
                    booster_number.save()
            # The system now looks for all user's that have used up all of the boosters that are assigned and removes them from the BoosterNumbers
            # model so they are not assigned any more boosters, to prevent the booster count from going below 0.
            booster_numbers_to_delete = BoosterNumbers.objects.filter(~Q(user__profile__boosters__gt=0))
            for booster_number in booster_numbers_to_delete:
                booster_number.delete()

            # Find the user that is at the top of the BoosterNumbers list and return them.
            oldest_booster_number = BoosterNumbers.objects.order_by('timestamp').first()
            # Once the system has found that user it the goes to check to see if there are any profiles to assign out on the BoostProfile list.
            # if there are profiles on the list with an active flag, it takes a random profile and assigns it to a user that has a booster to use.
            if oldest_booster_number:
                random_booster_profile = BoosterProfile.objects.order_by('?').first()
                if random_booster_profile:
                    random_booster_profile.user.profile.referred_by = oldest_booster_number.user
                    if random_booster_profile.user.profile.commission_owner is None:
                        random_booster_profile.user.profile.commission_owner = oldest_booster_number.user
                        random_booster_profile.user.profile.save()
                    self.stdout.write(f'Assigned a booster to {oldest_booster_number.user}.')
                    random_booster_profile.user.profile.is_booster = False
                    random_booster_profile.user.profile.save()

                    # Here we are updating the count of the boosters taking 1 away, and putting them at the back of the list so that they only get
                    # given one booster at a time. This keeps going till all the boosters are used up. Then the random user selection code will kick
                    # in, till people buy more boosters.
                    oldest_booster_number.user.profile.boosters -= 1
                    one_second_ago = timezone.now() - timedelta(seconds=1)
                    oldest_booster_number.timestamp = one_second_ago
                    oldest_booster_number.save()
                    oldest_booster_number.user.profile.save()

                    # Here we handel moving the money around on the ledgers.
                    add_ledger_entry(request, user=None, des=f'Membership Income assigned to {user.first_name} {user.last_name} ', debit=0, credit=37, ledger='Boosters', is_public=False)

            # Sleep for 1 seconds to allow the system to rest.
            time.sleep(1)
