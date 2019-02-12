from django.shortcuts import render, redirect
from django.http import HttpResponse
from .form import UserForm, HiddenForm
from .models import Booking, Merop
from django.core.mail import EmailMessage

from reportlab.pdfgen import canvas 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.lib.pagesizes import letter

import time

import rsa
import os


(pubkey, privkey) = rsa.newkeys(512)
import qrcode

def CreateQr():
	# Create qr code instance
	qr = qrcode.QRCode(
		version = 1,
		error_correction = qrcode.constants.ERROR_CORRECT_H,
		box_size = 4,
		border = 4,
	)

	# The data that you want to store
	data = "http://192.168.0.17:8000/brony"

	# Add data
	qr.add_data(data)
	qr.make(fit=True)

	# Create an image from the QR Code instance
	img = qr.make_image()

	# Save it somewhere, change the extension as needed:
	# img.save("image.png")
	# img.save("image.bmp")
	# img.save("image.jpeg")
	img.save("media/img/qrkode.jpg")






def PDF(merop, name, booked):
	packet = io.BytesIO()
	# create a new PDF with Reportlab
	MyFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
	pdfmetrics.registerFont(MyFontObject)
	MyCanvas = canvas.Canvas(packet, pagesize=letter)
	MyCanvas.setFont("Arial", 20)
	MyCanvas.drawString(178, 69, str(merop))
	MyCanvas.drawString(167, 101, setMestaforPdf('; '.join(booked)))
	MyCanvas.drawString(139, 35, str(name))
	MyCanvas.drawImage('media/img/qrkode.jpg', 400, 20)
	MyCanvas.save()

	#move to the beginning of the StringIO buffer
	packet.seek(0)
	new_pdf = PdfFileReader(packet)
	# read your existing PDF
	existing_pdf = PdfFileReader(open(r"media/pdf/ticket.pdf", "rb"))
	output = PdfFileWriter()
	# add the "watermark" (which is the new pdf) on the existing page
	page = existing_pdf.getPage(0)
	page.mergePage(new_pdf.getPage(0))
	output.addPage(page)
	# finally, write "output" to a real file
	outputStream = open(r"media/pdf/destination.pdf", "wb")
	output.write(outputStream)
	outputStream.close()

def Merop_list(request):
	zap = Merop.objects.in_bulk()
	kol = 0
	slov = {}
	for id in zap:
		kol+=1
		mass = []
		mass.append(zap[id].mero)
		mass.append(zap[id].place)
		mass.append(zap[id].date)
		mass.append(zap[id].image)
		#mass.append(zap[id].)
		slov[kol] = [mass]
	meropri = []
	places = []
	dates = []
	meropri_rsa = []
	images = []
	for i in slov.values():
		meropri.append(i[0][0])
		meropri_rsa.append(Crypto(i[0][0]))
	for i in slov.values():
		places.append(i[0][1])
	for i in slov.values():
		dates.append(i[0][2])
	for i in slov.values():
		images.append(i[0][3])
	return render(request, 'brony.html', {'meropri_rsa': meropri_rsa, 'places': places, 'dates': dates, 'slov': slov.values(), 'meropri': meropri, 'images': images})

def Crypto(some):
	some = rsa.encrypt(some.encode('utf-8'), pubkey)
	return str(some.hex())

def saver(request):
	merop = request.GET.get("merop")
	email = request.GET.get("email")
	places = request.GET.get("DataString")
	name = request.GET.get("name")
	return render(request, 'saver.html', {"email": email, "places": places, "merop": merop, "name": name})


def index(request):
	userform = UserForm()
	return render(request, 'index.html', {"form": userform})
	
def page(request):
	userform = UserForm()
	merop = request.GET.get("merop")
	return render(request, 'page.html', {"form": userform, "merop": (rsa.decrypt(bytes.fromhex(merop), privkey)).decode('utf-8')})

def contact(request):
	userform = UserForm()
	return render(request, 'contact.html', {"form": userform})
    
def query(request):
	if request.GET.get("Command")=="LoadBooking":
		DataString = ""
		merop = request.GET.get("merop")
		
		obj_merop = Merop.objects.get(pk = merop)
		
		zap = Booking.objects.in_bulk()
		for id in zap:
			if zap[id].mero == obj_merop: 
				DataString += zap[id].places + ","
		return HttpResponse(DataString)
    
	if request.GET.get("Command") == "Filler":
		merop = request.GET.get("merop")
		Fill = Merop(mero = merop)
		Fill.save()
		return HttpResponse('good')
	
	if request.GET.get("Command")=="SaveBooking":
		booked = request.GET.get("DataString")
		booked = str(booked).split(',')
        
        ################################
        #Booking.objects.all().delete()#
        ################################
        
		email = request.GET.get("email")
		name = request.GET.get("name")
		merop = request.GET.get("mero")
		
		print(email, name, merop)
		
		obj_merop = Merop.objects.get(pk = merop)
		
		#проверка на 5 мест
		k = 0
		prov = Booking.objects.in_bulk()
		for id in prov:
			if prov[id].email == email and prov[id].mero == obj_merop:
				k += 1
				if k >= 5:
					return HttpResponse("места")
		
		for i in booked:
			if Booking.objects.filter(places = i, mero = obj_merop).count() != 0:
				return HttpResponse("ошибка")
				
		for i in booked:
			book = Booking(username = name, email = email, places = i, mero = obj_merop)
			book.save()

		zap = Booking.objects.in_bulk()
		
		link = "http://127.0.0.1:8000/cancel/?email=" + Crypto(email) +"&"+ "merop=" + Crypto(merop)

		data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Demystifying Email Design</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link href="https://fonts.googleapis.com/css?family=Roboto+Mono" rel="stylesheet">
<body>
<style>
* {box-sizing: border-box;}
body {background: #1c3154; width:600px;}
.wedding {
  position: relative;
  height: 600px;
  max-width: 500px;
  margin: 50px auto 0;
  text-align: center;
}
.form-inner:before {
  display: inline-block;
  content: url(https://html5book.ru/wp-content/uploads/2017/05/form-flower.png);
}
.form-inner {
  padding: 0 40px 10px;
  margin-top: 45px;
  background: #1c3154;
  border-radius: 3px;
  box-shadow: 0 0 10px 4px #000;
}
.form-inner h2 {
  color: white;
  font-weight: 700;
  font-size: 70px;
  text-transform: uppercase;
  font-family: 'Roboto Mono', monospace;
}
.form-content {
  position: relative;
  background: #000;
}
.form-content:before {
  content: "";
  position: absolute;
  top: -4px;
  right: 0;
  left: 0;
  height: 2px;
  border-top: 1px solid #DDDDDD;
  border-bottom: 1px solid #DDDDDD;
}
.form-content h3 {
  font-family: 'Marck Script';
  font-size: 22px;
  color: #fff;
  font-weight: normal;
}
</style>
<form class="wedding">
  <div class="form-inner">
	<h2>PKCINEMA</h2>
    <div class="form-content">
      <h3>Ваше имя: ''' + str(name) + '''</h3>
      <h3>Ваши места : <p>''' + setMestaforEmail('<p>'.join(booked)) + '''</h3>
	  <h3> Отменить бронирование можно <a href=''' + str(link) + '''>тут</a></h3>
    </div>
  </div>
</form>
</body>
</head>
</html>'''
		
		PDF(merop, name, booked)
		CreateQr()
		
		email1 = EmailMessage('Бронирование', data, to=[str(email)])
		email1.content_subtype = "html"
		email1.attach_file(r'media/pdf/destination.pdf')
		email1.send()
        
		for id in zap: 
			print(zap[id].username, zap[id].email, zap[id].places, zap[id].mero)

		return HttpResponse("бронь")
    
	if request.GET.get("Command")=="DeleteBooking":
		Booking.objects.all().delete()
		return HttpResponse("Все места удалены, милорд")

def change(request):
		if request.GET.get("Command")=="LoadBooking":
			DataString = ""
			merop = request.GET.get("merop")
			email = request.GET.get("email")
			zap = Booking.objects.in_bulk()
			
			print(merop, email)
			
			obj_merop = Merop.objects.get(pk = merop)
			
			for id in zap:
				if zap[id].email == email and zap[id].mero == obj_merop: 
					DataString += zap[id].places + ","
			return HttpResponse(DataString)
            
		if request.GET.get("Command")=="CancelBooking":
			booked = request.GET.get("DataString")
			booked = str(booked).split(',')
			
			email = request.GET.get("email")
			merop = request.GET.get("mero")
			
			obj_merop = Merop.objects.get(pk = merop)
			
			data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Demystifying Email Design</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<body>
<style>
* {box-sizing: border-box;}
body {background: #FFF2E3;}
.wedding {
  position: relative;
  max-width: 350px;
  margin: 50px auto 0;
  text-align: center;
}
.form-inner:before {
  display: inline-block;
  margin-top: -45px;
  content: url(https://html5book.ru/wp-content/uploads/2017/05/form-flower.png);
}
.form-inner {
  padding: 0 40px 10px;
  margin-top: 45px;
  background: #ffffff;
  border-radius: 2px;
  box-shadow: 0 0 6px 1px rgba(0,0,0,.1);
}
.form-inner h2 {
  font-weight: 300;
  font-size: 20px;
  text-transform: uppercase;
  font-family: 'Cormorant Garamond', serif;
}
.form-content {
  position: relative;
  margin: 30px -40px 0 -40px;
  padding: 10px 40px 0 40px;
  background: #FFF8F3;
}
.form-content:before {
  content: "";
  position: absolute;
  top: -4px;
  right: 0;
  left: 0;
  height: 2px;
  border-top: 1px solid #DDDDDD;
  border-bottom: 1px solid #DDDDDD;
}
.form-content h3 {
  font-family: 'Marck Script', cursive;
  font-size: 22px;
  color: #898989;
  font-weight: normal;
}
.form-content input,
.form-content select {
  height: 38px;
  line-height: 38px;
  padding: 0 10px;
  background: #ffffff;
  border: 1px solid #DDDDDD;
  font-size: 20px;
  font-family: 'Cormorant Garamond', serif;
  color: #808080;
  outline: none;
}
.form-content input {width: 100%;}
.form-content input:focus,
.form-content select:focus {border-color: #C44D58;}
.form-content input[type="submit"] {
  margin: 20px 0;
  padding: 0 10px;
  background: #FF6B6B;
  color: #ffffff;   
  font-size: 18px;
  text-transform: uppercase;
  border-width: 0;
  border-radius: 20px;
  cursor: pointer;
  transition: .2s linear}
.form-content input[type="submit"]:hover {background: #C44D58;}
</style>
<form class="wedding">
  <div class="form-inner">
    <h2>Вы успешно отменили бронирование<br><h2>
    </div>
  </div>
</form>
</body>
</head>
</html>'''
		
		email1 = EmailMessage('Отмена Бронирования', data, to=[str(email)])
		email1.content_subtype = "html"
		email1.send()
			
		for i in booked:
			Booking.objects.filter(places = i, mero = obj_merop).delete()
		return HttpResponse("Ат души")

def cancel(request):
		hidform = HiddenForm()
		email = request.GET.get("email")
		merop = request.GET.get("merop")
		print(type(email))
		
		return render(request, "cancel.html", context={"email" : (rsa.decrypt(bytes.fromhex(email), privkey)).decode('utf-8'),"merop" : (rsa.decrypt(bytes.fromhex(merop), privkey)).decode('utf-8'), "form": hidform})
def setMestaforEmail(mesta):
		mesta = mesta.replace('s', 'место ')
		mesta = mesta.replace('_', ',')
		mesta = mesta.replace('r', ' ряд \n')
		return mesta
		
def setMestaforPdf(mesta):
		mesta = mesta.replace('s', 'место ')
		mesta = mesta.replace('_', ',')
		mesta = mesta.replace('r', ' ряд ')
		return mesta
        
def mail(request):
	if request.GET.get("Command")=="GetEmail":
		email = request.GET.get("email")
		usr = request.GET.get("usr")
		message = request.GET.get("message")
		data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Demystifying Email Design</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<body>
<style>
* {box-sizing: border-box;}
body {background: #FFF2E3;}
.wedding {
  position: relative;
  max-width: 350px;
  margin: 50px auto 0;
  text-align: center;
}
.form-inner:before {
  display: inline-block;
  margin-top: -45px;
  content: url(https://html5book.ru/wp-content/uploads/2017/05/form-flower.png);
}
.form-inner {
  padding: 0 40px 10px;
  margin-top: 45px;
  background: #ffffff;
  border-radius: 2px;
  box-shadow: 0 0 6px 1px rgba(0,0,0,.1);
}
.form-inner h2 {
  font-weight: 300;
  font-size: 20px;
  text-transform: uppercase;
  font-family: 'Cormorant Garamond', serif;
}
.form-content {
  position: relative;
  margin: 30px -40px 0 -40px;
  padding: 10px 40px 0 40px;
  background: #FFF8F3;
}
.form-content:before {
  content: "";
  position: absolute;
  top: -4px;
  right: 0;
  left: 0;
  height: 2px;
  border-top: 1px solid #DDDDDD;
  border-bottom: 1px solid #DDDDDD;
}
.form-content h3 {
  font-family: 'Marck Script', cursive;
  font-size: 22px;
  color: #898989;
  font-weight: normal;
}
.form-content input,
.form-content select {
  height: 38px;
  line-height: 38px;
  padding: 0 10px;
  background: #ffffff;
  border: 1px solid #DDDDDD;
  font-size: 20px;
  font-family: 'Cormorant Garamond', serif;
  color: #808080;
  outline: none;
}
.form-content input {width: 100%;}
.form-content input:focus,
.form-content select:focus {border-color: #C44D58;}
.form-content input[type="submit"] {
  margin: 20px 0;
  padding: 0 10px;
  background: #FF6B6B;
  color: #ffffff;   
  font-size: 18px;
  text-transform: uppercase;
  border-width: 0;
  border-radius: 20px;
  cursor: pointer;
  transition: .2s linear}
.form-content input[type="submit"]:hover {background: #C44D58;}
</style>
<form class="wedding">
  <div class="form-inner">
    <h2>От пользователей<br><h2>
    <div class="form-content">
      <h3>Почта отправителя: ''' + str(email) + '''</h3>
      <h3>Имя отправителя: ''' + str(usr) + '''</h3>
	  <h3>Его текст: ''' + str(message) + '''</h3> 
    </div>
  </div>
</form>
</body>
</head>
</html>'''
		email1 = EmailMessage('Служебка', data, to=['pkcinemaru@gmail.com'])
		email1.content_subtype = "html"
		email1.send()
		return HttpResponse("Fu")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
