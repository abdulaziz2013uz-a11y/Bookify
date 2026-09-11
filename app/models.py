from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Car(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Narxi"
    )
    description = models.TextField(verbose_name="Tavsifi")
    date = models.DateField(verbose_name="Sana")

    class Meta:
        verbose_name = "Mashina"
        verbose_name_plural = "Mashinalar"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    author = models.CharField(max_length=255, verbose_name="Muallif")
    genre = models.CharField(max_length=100, verbose_name="Janr")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Narxi"
    )
    description = models.TextField(verbose_name="Tavsif")
    published_date = models.DateField(verbose_name="Noshirlik sanasi")
    pages_count = models.PositiveIntegerField(
        default=0, verbose_name="Sahifalar soni"
    )
    content = models.TextField(blank=True, null=True, verbose_name="Mundarija")
    image = models.ImageField(
        upload_to="books/", blank=True, null=True, verbose_name="Rasm"
    )

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Kitob",
    )
    name = models.CharField(max_length=100, verbose_name="Ism")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Baho (1-5)",
    )
    comment = models.TextField(verbose_name="Izoh")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaratilgan vaqti"
    )

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.book.title} ({self.rating}★)"


class Order(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Kitob",
    )
    full_name = models.CharField(max_length=150, verbose_name="F.I.SH")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.CharField(max_length=255, verbose_name="Manzil")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Soni")
    is_confirmed = models.BooleanField(
        default=False, verbose_name="Tasdiqlangan"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaratilgan vaqti"
    )

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    @property
    def total_price(self):
        return self.book.price * self.quantity

    def __str__(self):
        return (
            f"{self.full_name} - {self.book.title} ({self.quantity} dona)"
        )