from django.urls import path
from admssadmin import views



urlpatterns = [
    path('admssadminhome/', views.admssadminhome, name="admssadminhome"),

    path('dashboardadmssadminnewloanreport/', views.dashboardadmssadminnewloanreport,name="dashboardadmssadminnewloanreport"),

    path('dashboardadmssadminemidepositreport/', views.dashboardadmssadminemidepositreport,name="dashboardadmssadminemidepositreport"),
  
    path('dashboardadmssadminemiduereport/', views.dashboardadmssadminemiduereport,name="dashboardadmssadminemiduereport"),
         
    path('admssadmincollemireportbranch/', views.admssadmincollemireportbranch,name="admssadmincollemireportbranch"),

    path('admssadminemiduereport/', views.admssadminemiduereport,name="admssadminemiduereport"),
         
    path('admssadminnewloanreport/', views.admssadminnewloanreport,name="admssadminnewloanreport"),

    path('admssadminprocessingfeereceipt/',views.admssadminprocessingfeereceipt, name="admssadminprocessingfeereceipt"),
    path('admssadminprocessingfeereceiptget/',views.admssadminprocessingfeereceiptget, name="admssadminprocessingfeereceiptget"),
    path('admssadminprocessingfeereceiptprint/',views.admssadminprocessingfeereceiptprint, name="admssadminprocessingfeereceiptprint"),


    path('admssadmingstdata/',views.admssadmingstdata, name="admssadmingstdata"),
    path('admssadminlicdata/',views.admssadminlicdata, name="admssadminlicdata"),
    path('admssadminupdatelicdata/',views.admssadminupdatelicdata, name="admssadminupdatelicdata"),

    
    path('admssadmincrifdata/',views.admssadmincrifdata, name="admssadmincrifdata"),
    path('admssadminauditmasterdata/',views.admssadminauditmasterdata, name="admssadminauditmasterdata"),

    path('admssadminchangetenure/',views.admssadminchangetenure, name="admssadminchangetenure"),
    path('admssadminchangetenureget/',views.admssadminchangetenureget, name="admssadminchangetenureget"), 
    path('admssadminchangetenurecommit/',views.admssadminchangetenurecommit, name="admssadminchangetenurecommit"), 

    
    path('admssadminsearch/',views.admssadminsearch, name="admssadminsearch"),
    path('admssadminupdate/',views.admssadminupdate, name="admssadminupdate"),
    path('admssadminupdatecommit/',views.admssadminupdatecommit, name="admssadminupdatecommit"),
    
    path('admssadmindeleteemi/',views.admssadmindeleteemi, name="admssadmindeleteemi"),
    path('admssadmindeleteemiget/<str:deletedata_transid>',views.admssadmindeleteemiget, name="admssadmindeleteemiget"),
    path('admssadmindeleteemicommit/',views.admssadmindeleteemicommit, name="admssadmindeleteemicommit"),

    path('admssadmindeletepayment/',views.admssadmindeletepayment, name="admssadmindeletepayment"),
    path('admssadmindeletepaymentget/<str:deletedata_transid>',views.admssadmindeletepaymentget, name="admssadmindeletepaymentget"),
    path('admssadmindeletepaymentcommit/',views.admssadmindeletepaymentcommit, name="admssadmindeletepaymentcommit"),


    path('admssadminusercreate/',views.admssadminusercreate, name="admssadminusercreate"),

    path('admssadminemicollectorreport/',views.admssadminemicollectorreport, name="admssadminemicollectorreport"),

    path('admssadminemicollectorreportget/',views.admssadminemicollectorreportget, name="admssadminemicollectorreportget"),
    
    path('admssadmininsuranceduereport/',views.admssadmininsuranceduereport, name="admssadmininsuranceduereport"),

    path('authcenterexpance/',views.authcenterexpance, name="authcenterexpance"),

    
    path('admssadmineod/', views.admssadmineod, name="admssadmineod"),
    
    path('admssadminlogout/', views.admssadminlogout, name="admssadminlogout"),

]



