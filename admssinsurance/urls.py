from django.urls import path
from admssinsurance import views

urlpatterns = [
    path('admssinsurancehome/', views.admssinsurancehome, name="admssinsurancehome"),
 
    path('admssinsurancelogout/', views.admssinsurancelogout, name="admssinsurancelogout"),

]



