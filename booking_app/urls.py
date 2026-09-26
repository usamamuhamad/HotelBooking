from django.urls import path
from .views import home
from . import views 
from django.contrib import admin
from django.urls import path, include
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('admin', admin.site.urls),
    path('', home, name="home"),
    path('', views.home, name='home'),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('get-hotels/', views.get_hotels, name='get_hotels'),
    path('success/', views.success, name='success'),
    path('contact/', views.contact, name='contact'),  
    path('about/', views.about, name='about'),
    path('support/', views.support, name='support'),
    path('hotels/', views.hotels, name='hotels'),
    path('hotels/<str:city>/', views.hotels_by_city, name='hotels_by_city'),
    path("submit-feedback/<int:hotel_id>/", views.submit_feedback, name="submit_feedback"),
    path("save-booking/", views.save_booking, name="save_booking"),    
    
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)