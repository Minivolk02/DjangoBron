from django.contrib import admin
from .models import Booking, Merop, Vstavka

@admin.register(Booking)

class BookingAdmin(admin.ModelAdmin):
   list_display = ('username', 'email', 'places', 'mero')

@admin.register(Merop)

class MeropAdmin(admin.ModelAdmin):
    list_display = ('mero', 'place', 'date')

@admin.register(Vstavka)

class MeropVstavka(admin.ModelAdmin):
	list_display = ('id', 'name')