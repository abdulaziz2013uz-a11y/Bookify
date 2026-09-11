import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .models import Book, Order, Review


def is_admin(user):
    return user.is_staff


# ==========================================
# 📊 DASHBOARD VIEW
# ==========================================
@user_passes_test(is_admin, login_url="/login/")
def admin_dashboard(request):
    stats = Book.objects.aggregate(
        total_price=Sum("price"),
        avg_price=Avg("price"),
    )

    context = {
        "total_books": Book.objects.count(),
        "total_orders": Order.objects.count(),
        "total_reviews": Review.objects.count(),
        "total_price": stats["total_price"] or 0,
        "avg_price": stats["avg_price"] or 0,
        "recent_books": Book.objects.all().order_by("-id")[:5],
        "recent_orders": Order.objects.all().order_by("-created_at")[:5],
    }
    return render(request, "admin_dashboard.html", context)


# ==========================================
# ⚙️ SOZLAMALAR
# ==========================================
@user_passes_test(is_admin, login_url="/login/")
def system_settings(request):
    context = {
        "total_books": Book.objects.count(),
        "total_orders": Order.objects.count(),
        "total_reviews": Review.objects.count(),
    }
    return render(request, "system_settings.html", context)


# ==========================================
# 📚 BOOKS VIEWS
# ==========================================
def books(request):
    books_list = Book.objects.all()

    query = request.GET.get("q")
    if query:
        books_list = books_list.filter(title__icontains=query)

    sort = request.GET.get("sort")
    if sort == "price_asc":
        books_list = books_list.order_by("price")
    elif sort == "price_desc":
        books_list = books_list.order_by("-price")
    elif sort == "title":
        books_list = books_list.order_by("title")

    stats = Book.objects.aggregate(
        total_price=Sum("price"),
        avg_price=Avg("price"),
    )

    context = {
        "books": books_list,
        "query": query or "",
        "sort": sort or "",
        "total_count": Book.objects.count(),
        "total_price": stats["total_price"] or 0,
        "avg_price": stats["avg_price"] or 0,
    }

    if request.user.is_authenticated and request.user.is_staff:
        return render(request, "books_list.html", context)
    return render(request, "public_books.html", context)


def book_create(request):
    if request.method == "POST":
        nomi = request.POST.get("title")
        muallif = request.POST.get("author")
        janr = request.POST.get("genre")
        narxi = request.POST.get("price")
        tavsif = request.POST.get("description")
        sana = request.POST.get("published_date")
        sahifa = request.POST.get("pages_count")
        matn = request.POST.get("content")
        image = request.FILES.get("image")

        Book.objects.create(
            title=nomi,
            author=muallif,
            genre=janr,
            price=narxi,
            description=tavsif,
            published_date=sana,
            pages_count=sahifa,
            content=matn,
            image=image,
        )
        return redirect("books_list")

    return render(request, "books_create.html")


def book_detail(request, pk):
    book = get_object_or_404(Book, id=pk)
    reviews_list = book.reviews.all().order_by("-created_at")

    if request.method == "POST":
        name = request.POST.get("name")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        Review.objects.create(
            book=book, name=name, rating=rating, comment=comment
        )
        return redirect("book_detail", pk=book.id)

    avg_rating = (
        reviews_list.aggregate(Avg("rating"))["rating__avg"] or 0
    )

    context = {
        "book": book,
        "reviews": reviews_list,
        "avg_rating": avg_rating,
        "reviews_count": reviews_list.count(),
    }

    if request.user.is_authenticated and request.user.is_staff:
        return render(request, "books_detail.html", context)
    return render(request, "public_book_detail.html", context)


@user_passes_test(is_admin, login_url="/login/")
def books_update(request, pk):
    book = get_object_or_404(Book, id=pk)
    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.genre = request.POST.get("genre")
        book.price = request.POST.get("price")
        book.description = request.POST.get("description")
        book.published_date = request.POST.get("published_date")
        book.pages_count = request.POST.get("pages_count")
        book.content = request.POST.get("content")

        if request.FILES.get("image"):
            book.image = request.FILES.get("image")

        book.save()
        return redirect("books_list")
    return render(request, "books_update.html", {"book": book})


@user_passes_test(is_admin, login_url="/login/")
def book_delete(request, pk):
    book = get_object_or_404(Book, id=pk)
    book.delete()
    return redirect("books_list")


@user_passes_test(is_admin, login_url="/login/")
def books_import(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Fayl tanlanmadi.")
            return redirect("books_import")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Faqat .csv fayl yuklang.")
            return redirect("books_import")

        decoded_file = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))

        added = 0
        skipped = 0

        for row in reader:
            try:
                Book.objects.create(
                    title=row["title"],
                    author=row["author"],
                    genre=row["genre"],
                    price=row["price"],
                    description=row.get("description", ""),
                    published_date=row["published_date"],
                    pages_count=row["pages_count"],
                    content=row.get("content", ""),
                )
                added += 1
            except Exception:
                skipped += 1

        messages.success(
            request,
            f"{added} ta kitob qo'shildi, {skipped} ta qator o'tkazib yuborildi.",
        )
        return redirect("books_list")

    return render(request, "books_import.html")


def order_create(request, pk):
    book = get_object_or_404(Book, id=pk)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        quantity = request.POST.get("quantity")

        Order.objects.create(
            book=book,
            full_name=full_name,
            phone=phone,
            address=address,
            quantity=quantity,
        )
        messages.success(
            request,
            "Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        )
        return redirect("book_detail", pk=book.id)

    return render(request, "order_create.html", {"book": book})


# ==========================================
# 📌 YANGI BO'LIMLAR VIEWS
# ==========================================
@user_passes_test(is_admin, login_url="/login/")
def warehouse(request):
    books = Book.objects.all()
    return render(request, "warehouse.html", {"books": books})


@user_passes_test(is_admin, login_url="/login/")
def reviews(request):
    reviews_list = Review.objects.select_related("book").all().order_by("-id")
    return render(request, "reviews.html", {"reviews": reviews_list})


@user_passes_test(is_admin, login_url="/login/")
def payments(request):
    orders = Order.objects.select_related("book").all().order_by("-id")
    return render(request, "payments.html", {"orders": orders})


@user_passes_test(is_admin, login_url="/login/")
def readers(request):
    orders = Order.objects.select_related("book").all().order_by("-id")
    return render(request, "readers.html", {"orders": orders})


# ==========================================
# 👤 ADMINLAR
# ==========================================
@user_passes_test(is_admin, login_url="/login/")
def admins(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu foydalanuvchi nomi band.")
        elif not username or not password:
            messages.error(request, "Login va parolni kiriting.")
        elif " " in username:
            messages.error(request, "Login probel (bo'sh joy) o'z ichiga olmasligi kerak.")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
            )
            messages.success(request, f"'{username}' admin sifatida qo'shildi.")
        return redirect("admins")

    admin_list = User.objects.filter(is_staff=True).order_by("-date_joined")
    return render(request, "admins.html", {"admins": admin_list})


@user_passes_test(is_admin, login_url="/login/")
def admin_remove(request, pk):
    target = get_object_or_404(User, id=pk)

    if target == request.user:
        messages.error(request, "O'zingizni adminlikdan chiqara olmaysiz.")
    elif target.is_superuser:
        messages.error(request, "Superadminni olib tashlab bo'lmaydi.")
    else:
        target.is_staff = False
        target.save()
        messages.success(request, f"'{target.username}' adminlikdan chiqarildi.")

    return redirect("admins")