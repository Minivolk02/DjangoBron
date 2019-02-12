from django.db import models

class Vstavka(models.Model):
	name = models.CharField(max_length=30)

class Merop(models.Model):
	mero = models.CharField(max_length=100, primary_key = True)
	date = models.DateField(null = True)
	place = models.CharField(default = "Улица", max_length=30)
	image = models.ImageField(upload_to='img/', blank=True)
 
class Booking(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    places = models.CharField(max_length=30)
    mero = models.ForeignKey(Merop, on_delete = models.CASCADE)