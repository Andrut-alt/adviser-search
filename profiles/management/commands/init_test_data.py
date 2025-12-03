from django.core.management.base import BaseCommand
from profiles.models import Department, ScientificInterest


class Command(BaseCommand):
    help = 'Створює тестові дані: кафедри та наукові інтереси'

    def handle(self, *args, **options):
        self.stdout.write('Створення тестових даних...')

        # Створюємо кафедри
        departments = [
            'Кафедра інформаційних систем',
            'Кафедра комп\'ютерних наук',
            'Кафедра програмної інженерії',
            'Кафедра математики',
            'Кафедра фізики',
            'Кафедра економіки',
        ]

        for dept_name in departments:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Створено кафедру: {dept_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Кафедра вже існує: {dept_name}'))

        # Створюємо наукові інтереси
        interests = [
            'Машинне навчання',
            'Веб-розробка',
            'Бази даних',
            'Кібербезпека',
            'Мобільні додатки',
            'Штучний інтелект',
            'Data Science',
            'Blockchain',
            'Cloud Computing',
            'DevOps',
        ]

        for interest_name in interests:
            interest, created = ScientificInterest.objects.get_or_create(name=interest_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Створено науковий інтерес: {interest_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Науковий інтерес вже існує: {interest_name}'))

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно створено!'))

