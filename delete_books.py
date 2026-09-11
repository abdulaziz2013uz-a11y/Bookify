import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import Book

# ID si 1, 2, 3, 4, 5 bo'lmagan barcha kitoblarni o'chirish
deleted_count, _ = Book.objects.exclude(id__in=[1, 2, 3, 4, 5]).delete()
print(f"{deleted_count} ta ortiqcha kitob muvaffaqiyatli o'chirildi!")