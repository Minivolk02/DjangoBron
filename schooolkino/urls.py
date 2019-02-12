from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from bron import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('cancel/', views.cancel, name = 'cancel'),
	
	#Обращения к brony
	path('brony/', views.Merop_list, name = 'Merop_list'),
	path('brony/page/', views.page, name = 'page'),
	path('brony/page/query', views.query, name = 'pagequery'),
	path('brony/page/saver', views.saver, name = 'pagesaver'),
	
	#Обращения к change
	path('change/', views.change, name = 'change'),
	
	path('contact/', views.contact, name = 'contact'),
    
	path('', views.index, name='index'),
    
	#обращения к query
	path('query/', views.query, name='query'),
    path('page/query/', views.query, name='query'),
	path('contact/mail/', views.mail, name='mail'),
	
	#Обращения к admin
	path('admin/', admin.site.urls)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
