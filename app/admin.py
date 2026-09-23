from django.contrib import admin

from .models import Shifoxona


@admin.register(Shifoxona)
class ShifoxonaAdmin(admin.ModelAdmin):
	list_display = (
		"nomi",
		"manzili",
		"xona_soni",
		"shifokor_soni",
		"bahosi",
		"ochiqmi",
	)
	search_fields = ("nomi", "manzili", "emaili")
