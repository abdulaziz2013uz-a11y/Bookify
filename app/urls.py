from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    # Dashboard (Bosh sahifa)
    path("", views.admin_dashboard, name="admin_dashboard"),
    # Kitoblar bo'limi
    path("books/", views.books, name="books_list"),
    path("books/create/", views.book_create, name="book_create"),
    path("books/import/", views.books_import, name="books_import"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/update/", views.books_update, name="books_update"),
    path("books/delete/<int:pk>/", views.book_delete, name="book_delete"),
    path("books/<int:pk>/order/", views.order_create, name="order_create"),
    # Yangi bo'limlar
    path("warehouse/", views.warehouse, name="warehouse"),
    path("reviews/", views.reviews, name="reviews"),
    path("payments/", views.payments, name="payments"),
    path("readers/", views.readers, name="readers"),
    # Sozlamalar
    path("settings/", views.system_settings, name="system_settings"),
    path("admins/", views.admins, name="admins"),
    path("admins/<int:pk>/remove/", views.admin_remove, name="admin_remove"),
    # Parolni o'zgartirish
    path(
        "settings/password/",
        auth_views.PasswordChangeView.as_view(
            template_name="password_change.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "settings/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/books/"), name="logout"),
]