import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import random
from faker import Faker
from app.models import Book

fake = Faker()
janrlar = ["Roman", "Tarixiy", "Detektiv", "Fantastika", "Psixologiya", "Sarguzasht"]

kitoblar = []
print("1000 ta kitob shakllantirilmoqda...")

for _ in range(1000):
    kitoblar.append(
        Book(
            title=fake.sentence(nb_words=3).replace('.', ''),
            author=fake.name(),
            genre=random.choice(janrlar),
            price=random.randint(25, 150) * 1000,
            published_date=fake.date_between(start_date='-30y', end_date='today'),
            description=fake.paragraph(nb_sentences=3),
            content=fake.text(max_nb_chars=500)
        )
    )

Book.objects.bulk_create(kitoblar)
print("1000 ta kitob muvaffaqiyatli qo'shildi!")