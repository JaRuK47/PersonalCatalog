import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from venue.models import Venue, Session, Booking, Round, RoundPlayer, GameMode

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])

        #Booking.objects.all().delete()
        #RoundPlayer.objects.all().delete()
        #Round.objects.all().delete()
        #Session.objects.all().delete()
        #Venue.objects.all().delete()
        #GameMode.objects.all().delete()
        #User.objects.exclude(is_superuser=True).delete()
        mode = GameMode.objects.create(name="Спортивная мафия")
        venues = [Venue.objects.create(name=fake.company(), address=fake.address()) for _ in range(10)]
        sessions = [Session.objects.create(venue=random.choice(venues), date=fake.date(), start_time=fake.time(), title="Игра", game_mode=mode) for _ in range(100)]
        users = [User.objects.create_user(username=fake.unique.user_name(), password="123") for _ in range(100)]
        rounds = []
        for s in sessions:
            winning_team = random.choice(['mafia', 'town'])
            rounds.append(Round.objects.create(
                session=s, number=1, host=random.choice(users), game_mode=mode, winning_team=winning_team
            ))

        for _ in range(1000):
            Booking.objects.create(
                user=random.choice(users),
                session=random.choice(sessions),
                status='active'
            )

        roles = ['Мафия', 'Дон', 'Шериф', 'Доктор', 'Мирный', 'Мирный', 'Мирный']
        mafia_roles = ['Мафия', 'Дон']

        for r in rounds:
            players_for_round = random.sample(users, 10)
            for p in players_for_round:
                role = random.choice(roles)
                is_mafia = role in mafia_roles

                won = False
                if r.winning_team == 'mafia' and is_mafia:
                    won = True
                if r.winning_team == 'town' and not is_mafia:
                    won = True

                RoundPlayer.objects.create(
                    round=r,
                    user=p,
                    role=role,
                    points=round(random.uniform(0, 5), 1),
                    won=won
                )