from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Налаштовує Site для django-allauth'

    def handle(self, *args, **options):
        # Отримуємо або створюємо Site з ID=2 (як в settings.py)
        site, created = Site.objects.get_or_create(
            id=2,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Local Development',
            }
        )
        
        if not created:
            # Оновлюємо існуючий Site
            site.domain = 'localhost:8000'
            site.name = 'Local Development'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Оновлено Site (ID={site.id}): {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Створено Site (ID={site.id}): {site.domain}'))

