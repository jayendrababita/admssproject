from django.urls import path
from admsscoll import views


urlpatterns = [
    path('admsscollhome/', views.admsscollhome, name="admsscollhome"),
    path('collemideposit/', views.collemideposit, name="collemideposit"),
    path('collemicommit/', views.collemicommit, name="collemicommit"),
    path('collgroupemideposit/', views.collgroupemideposit, name="collgroupemideposit"),
    path('collgroupemidepositget/', views.collgroupemidepositget,name="collgroupemidepositget"),
    path('collgroupemidepositcommit/', views.collgroupemidepositcommit, name="collgroupemidepositcommit"),
    path('collemireport/', views.collemireport, name="collemireport"),
    path('collemireportall/', views.collemireportall, name="collemireportall"),
    path('collemipendingreport/', views.collemipendingreport,name="collemipendingreport"),
    path('collloanledger/', views.collloanledger, name="collloanledger"),
    path('collloanlist/', views.collloanlist, name="collloanlist"),
    path('collnewloanreport/', views.collnewloanreport, name="collnewloanreport"),
    path('collsettledloanreport/', views.collsettledloanreport, name="collsettledloanreport"),
    path('admsscolllogout/', views.admsscolllogout, name="admsscolllogout"),

]
