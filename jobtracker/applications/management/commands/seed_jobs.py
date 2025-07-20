from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from applications.models import JobApplication, Company, Tag
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed the database with fake job applications for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        statuses = ['AP', 'HR', 'TT', 'IN', 'OF', 'RJ', 'AC']
        sources = ['LN', 'IN', 'GH', 'WS', 'RF', 'OT']

        # Use your actual user 'anony' for testing visibility
        user = User.objects.filter(username='anony').first()
        if not user:
            user = User.objects.create_user(username='anony', password='password123')
            self.stdout.write(self.style.SUCCESS('✅ Created user "anony" with password "password123".'))

        # Create 5 fake companies if none exist
        if Company.objects.count() == 0:
            for _ in range(5):
                Company.objects.create(
                    name=fake.company(),
                    website=fake.url(),
                    glassdoor_rating=round(random.uniform(2.0, 5.0), 1),
                    notes=fake.text(max_nb_chars=100)
                )
            self.stdout.write(self.style.SUCCESS('✅ Created 5 fake companies.'))

        companies = list(Company.objects.all())

        for _ in range(50):
            company = random.choice(companies)
            job = JobApplication.objects.create(
                user=user,
                company=company,
                position=fake.job(),
                status=random.choice(statuses),
                source=random.choice(sources),
                applied_date=fake.date_between(start_date='-6M', end_date='today'),
                notes=fake.text(max_nb_chars=100),
                salary_min=random.choice([None, 3000, 4000, 5000]),
                salary_max=random.choice([None, 6000, 7000, 8000]),
                is_remote=random.choice([True, False]),
                referral_contact=fake.name() if random.choice([True, False]) else ''
            )
            print(f"Created: {job.company.name} - {job.position}")

        self.stdout.write(self.style.SUCCESS('✅ Successfully added 50 fake job applications linked to user "anony"!'))
