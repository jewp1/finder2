from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Convert passlib bcrypt hashes to Django BCryptSHA256PasswordHasher format'

    def handle(self, *args, **options):
        users = User.objects.values('id', 'password')
        updated = 0

        for row in users:
            pw = row['password']
            if pw and (pw.startswith('$2b$') or pw.startswith('$2a$')):
                new_pw = f'bcrypt_sha256$${pw}'
                User.objects.filter(id=row['id']).update(password=new_pw)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} password hashes.'))
