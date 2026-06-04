from django.urls import path
from admssapp import views
from django.contrib import admin


urlpatterns = [

    path('', views.home, name="home"),
    path('login', views.login, name="login"),
    path('resetlogin/', views.resetlogin, name="resetlogin"),


    path('newloan/', views.newloan, name="newloan"),
    path('addnewloan/', views.addnewloan, name="addnewloan"),

    path('loansettlement/', views.loansettlement, name="loansettlement"),
    path('loansettlementcommit/', views.loansettlementcommit, name="loansettlementcommit"),

    path('loanforceclosure/', views.loanforceclosure, name="loanforceclosure"),
    path('loanforceclosurecommit/', views.loanforceclosurecommit, name="loanforceclosurecommit"),


    path('loanmaster/', views.loanmaster, name="loanmaster"),

    path('updatemaster/', views.updatemaster, name="updatemaster"),
    path('updatemastercommit/', views.updatemastercommit, name="updatemastercommit"),

    path('noccertificate/', views.noccertificate, name="noccertificate"),

    path('emicalculator/', views.emicalculator, name="emicalculator"),
    
    path('loaninsurclaim/', views.loaninsurclaim, name="loaninsurclaim"),
    path('loaninsurclaimcommit/', views.loaninsurclaimcommit, name="loaninsurclaimcommit"),

    path('loaninsurfundreceive/', views.loaninsurfundreceive, name="loaninsurfundreceive"),
    path('loaninsurfundreceivecommit/', views.loaninsurfundreceivecommit, name="loaninsurfundreceivecommit"),

    

    
    path('newloanreport/', views.newloanreport, name="newloanreport"),
    path('dashboardnewloanreport/', views.dashboardnewloanreport, name="dashboardnewloanreport"),

    path('settledloanreport/', views.settledloanreport, name="settledloanreport"),
    path('dashboardsettledloanreport/', views.dashboardsettledloanreport, name="dashboardsettledloanreport"),

    path('nearsettlereport/', views.nearsettlereport, name="nearsettlereport"),

    path('emiduereport/', views.emiduereport, name="emiduereport"),
    path('dashboardemiduereport/', views.dashboardemiduereport, name="dashboardemiduereport"),

    path('emidepositreport/', views.emidepositreport, name="emidepositreport"),
    path('dashboardemidepositreport/', views.dashboardemidepositreport, name="dashboardemidepositreport"),

  
    path('loanledger/', views.loanledger, name="loanledger"),
    path('loanledgersettlement/', views.loanledgersettlement, name="loansettlementreport"),
 
    path('transreport/', views.transreport, name="transreport"),
    path('loanstatistics/', views.loanstatistics, name="loanstatistics"),
    path('comprativeloanstatistics/', views.comprativeloanstatistics, name="comprativeloanstatistics"),
    path('groupwiselist/', views.groupwiselist, name="groupwiselist"),
    path('emicollectorreport/', views.emicollectorreport, name="emicollectorreport"),
    path('emicollectorwiselist/', views.emicollectorwiselist, name="emicollectorwiselist"),
    path('emicollectorwisependinglist/', views.emicollectorwisependinglist, name="emicollectorwisependinglist"),
    path('emisummarywiselist/', views.emisummarywiselist, name="emisummarywiselist"),

    path('loanidadminwiselist/', views.loanidadminwiselist, name="loanidadminwiselist"),
    path('loanidadminsummary/', views.loanidadminsummary, name="loanidadminsummary"),
    path('loanidadminsummaryreport/', views.loanidadminsummaryreport, name="loanidadminsummaryreport"),
    path('loanidcollectorsummary/', views.loanidcollectorsummary, name="loanidcollectorsummary"),
    
    path('emidefaultreport/', views.emidefaultreport, name="emidefaultreport"),
    
   

    path('associatereport/', views.associatereport, name="associatereport"),


    path('autocomplete/', views.autocomplete, name="autocomplete"),
    path('autocompletenoc/', views.autocompletenoc, name="autocompletenoc"),
    path('masterautocomplete/', views.masterautocomplete, name="masterautocomplete"),   


    path('emideposit/', views.emideposit, name="emideposit"),
    path('emicommit/', views.emicommit, name="emicommit"),

    path('emispecialdeposit/', views.emispecialdeposit, name="emispecialdeposit"),
    path('emispecialtcommit/', views.emispecialtcommit, name="emispecialtcommit"),

    path('groupemideposit/', views.groupemideposit, name="groupemideposit"),
    path('groupemidepositget/', views.groupemidepositget,name="groupemidepositget"),

    path('groupemidepositupdate/<str:emicolldata_id>',views.groupemidepositupdate, name="groupemidepositupdate"),
    path('groupemidepositupdatecommit/', views.groupemidepositupdatecommit,name="groupemidepositupdatecommit"),
    
    path('groupemidepositdelete/<str:emicolldata_id>',views.groupemidepositdelete, name="groupemidepositdelete"),
    path('groupemidepositdeletecommit/', views.groupemidepositdeletecommit,name="groupemidepositdeletecommit"),
    
    path('groupemidepositcommit/', views.groupemidepositcommit,name="groupemidepositcommit"),


    path('collemidepositbranch/', views.collemidepositbranch, name="collemidepositbranch"),
    path('collemiprocessbranch/', views.collemiprocessbranch, name="collemiprocessbranch"),
    path('collemifinalbranch/', views.collemifinalbranch, name="collemifinalbranch"),

    path('emisundry/', views.emisundry, name="emisundry"),
    path('emisundryprocess/', views.emisundryprocess, name="emisundryprocess"),
    path('emisundryprocessget/<str:sundry_id>',views.emisundryprocessget,name="emisundryprocessget"),
    path('emisundryprocesscommit/',views.emisundryprocesscommit,name="emisundryprocesscommit"),




    path('emireceipt/', views.emireceipt, name="emireceipt"),
    path('emireceiptloanid/', views.emireceiptloanid, name="emireceiptloanid"),
    path('emireceiptloanidget/', views.emireceiptloanidget,name="emireceiptloanidget"),

    path('collemidepositupdate/<str:emicolldata_id>',views.collemidepositupdate,name="collemidepositupdate"),
    path('collemidepositupdatecommit/',views.collemidepositupdatecommit,name="collemidepositupdatecommit"),

    path('collemidepositdelete/<str:emicolldata_id>',views.collemidepositdelete,name="collemidepositdelete"),
    path('collemidepositdeletecommit/',views.collemidepositdeletecommit,name="collemidepositdeletecommit"),

    path('banktrans/', views.banktrans, name="banktrans"),
    path('banktransac/', views.banktransac, name="banktransac"),
    path('banktransaccommit/', views.banktransaccommit, name="banktransaccommit"),

    path('bankcharges/', views.bankcharges, name="bankcharges"),
    path('bankdishonor/', views.bankdishonor, name="bankdishonor"),
    path('banktransreport/', views.banktransreport, name="banktransreport"),
   
    path('bankvoucharprint/', views.bankvoucharprint, name="bankvoucharprint"),
    path('bankvoucharprintshow/', views.bankvoucharprintshow, name="bankvoucharprintshow"),
     
    path('bankintrest/', views.bankintrest, name="bankintrest"),
 
    path('fundin/', views.fundin, name="fundin"),
    path('fundinoth/', views.fundinoth, name="fundinoth"),



    path('fundout/', views.fundout, name="fundout"),
    path('fundloan/', views.fundloan, name="fundloan"),
    path('fundloanrecovery/', views.fundloanrecovery, name="fundloanrecovery"),
    path('fundloanrecoverylist/<str:loanid>', views.fundloanrecoverylist, name="fundloanrecoverylist"),    
    path('fundloanrecoverycommit/', views.fundloanrecoverycommit, name="fundloanrecoverycommit"),     
    
    path('investorpaymentfundget/<str:transid>',views.investorpaymentfundget, name="investorpaymentfundget"), 
    path('investorpaymentfundcommit/', views.investorpaymentfundcommit, name="investorpaymentfundcommit"),
    
    path('fundpayment/', views.fundpayment, name="fundpayment"),
    path('fundpaymentget/', views.fundpaymentget, name="fundpaymentget"),
    path('fundpaymentcommit/', views.fundpaymentcommit, name="fundpaymentcommit"),
    path('fundactivereport/', views.fundactivereport, name="fundactivereport"),
    path('fundmisactivereport/', views.fundmisactivereport, name="fundmisactivereport"),
        
    #path('fundtransactionreport/', views.fundtransactionreport, name="fundtransactionreport"),
    path('emifundtransactionreport/', views.emifundtransactionreport,name="emifundtransactionreport"),
    path('emifundtransactionledger/<str:fundid>',views.emifundtransactionledger, name="emifundtransactionledger"),

    path('fundtransfersend/', views.fundtransfersend, name="fundtransfersend"),
    path('fundtransfersendcommit/', views.fundtransfersendcommit,name="fundtransfersendcommit"),
  
    path('fundtransferreceive/', views.fundtransferreceive,name="fundtransferreceive"),
    path('fundtransferreceivecommit/', views.fundtransferreceivecommit,name="fundtransferreceivecommit"),

    path('fundtransfersendreceivereport/', views.fundtransfersendreceivereport,name="fundtransfersendreceivereport"),

    path('fundtransfersendnormal/', views.fundtransfersendnormal, name="fundtransfersendnormal"),
    path('fundtransferreceivenormal/', views.fundtransferreceivenormal, name="fundtransferreceivenormal"),
    path('fundtransferreceivecommitnormal/', views.fundtransferreceivecommitnormal, name="fundtransferreceivecommitnormal"),
    path('miscpayment/', views.miscpayment, name="miscpayment"),
    
    path('miscpaymentreport/', views.miscpaymentreport, name="miscpaymentreport"),
    path('miscsummaryreport/', views.miscsummaryreport, name="miscsummaryreport"),
    path('miscvoucharprint/', views.miscvoucharprint, name="miscvoucharprint"),
    path('miscvoucharprintshow/', views.miscvoucharprintshow, name="miscvoucharprintshow"),
    
    path('assoexppayment/', views.assoexppayment, name="assoexppayment"),
    path('assoexppaymentget/', views.assoexppaymentget, name="assoexppaymentget"),    
    path('assoexppaymentcommit/', views.assoexppaymentcommit, name="assoexppaymentcommit"),    
    path('assoexppaymentreport/', views.assoexppaymentreport, name="assoexppaymentreport"),
    
    path('advancepayment/', views.advancepayment, name="advancepayment"),
    path('advancepaymentcredit/', views.advancepaymentcredit, name="advancepaymentcredit"),
    path('advancepaymentcreditlist/<str:advanceid>',views.advancepaymentcreditlist, name="advancepaymentcreditcommitlist"),    
    path('advancepaymentcreditcommit/',views.advancepaymentcreditcommit, name="advancepaymentcreditcommit"),    
    
    path('authcenterexpensepayment/',views.authcenterexpensepayment, name="authcenterexpensepayment"),
    path('authcenterexpensepaymentcommit/', views.authcenterexpensepaymentcommit,name="authcenterexpensepaymentcommit"),

    path('collemireportbranch/', views.collemireportbranch, name="collemireportbranch"),

    path('whatsappdaydata/', views.whatsappdaydata, name="whatsappdaydata"),
    path('whatsappmessage/', views.whatsappmessage, name="whatsappmessage"),
    path('whatsappmessageget/', views.whatsappmessageget, name="whatsappmessageget"),


    path('loanleadnew/', views.loanleadnew, name="loanleadnew"),
    path('loanleadnewget/', views.loanleadnewget, name="loanleadnewget"),
    path('loanleadnewcommit/', views.loanleadnewcommit, name="loanleadnewcmmit"),

    path('loanleadupdate/<str:loanlead_id>',views.loanleadupdate,name="loanleadupdate"),
    path('loanleadupdate/',views.loanleadupdate,name="loanleadupdate"),
    path('loanleadupdateget/',views.loanleadupdateget,name="loanleadupdateget"),

    path('loanlead1updatecommit/',views.loanlead1updatecommit,name="loanlead1updatecommit"),

    path('loanlead2updatecommit/',views.loanlead2updatecommit,name="loanlead2updatecommit"),

    path('loanlead3updatecommit/',views.loanlead3updatecommit,name="loanlead3updatecommit"),

    path('loanlead4updatecommit/',views.loanlead4updatecommit,name="loanlead4updatecommit"),

    path('loanleaddeletecommit/', views.loanleaddeletecommit, name="loanleaddeletecommit"),

    path('loanleadreport/', views.loanleadreport, name="loanleadreport"),
    path('loanleaddetail/<str:loanlead_id>/', views.loanleaddetail, name="loanleaddetail"),

    path('logout/', views.logout, name="logout"),
    
]
