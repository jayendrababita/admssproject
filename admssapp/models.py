from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.contrib.sessions.models import Session


class Locationlogin(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    rpersoncode = models.CharField(max_length=10,null=True,blank=True)
    rpersonname = models.CharField(max_length=50,null=True,blank=True)
    rundate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
    lastlogin = models.DateTimeField(auto_now=True,null=True,blank=True)
    ip = models.CharField(max_length=50,null=True,blank=True)
    loannum = models.IntegerField(null=True,blank=True,default=0)
    loangroupid = models.IntegerField(null=True,blank=True,default=0)
    lastloanid = models.CharField(max_length=13,null=True,blank=True)
    transidnum = models.IntegerField(null=True,blank=True,default=0)
    lasttransid = models.CharField(max_length=13,null=True,blank=True)
    perc = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
    status = models.CharField(max_length=1,null=True,blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.locationname


class Opclcashbank(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True)
    bankac = models.CharField(max_length=20,null=True,blank=True)
    bankacname = models.CharField(max_length=50,null=True,blank=True)
    bankname = models.CharField(max_length=50,null=True,blank=True)
    bankcode = models.CharField(max_length=4,null=True,blank=True)
    bankbranch = models.CharField(max_length=100,null=True,blank=True)
    bankifsc = models.CharField(max_length=20,null=True,blank=True)
    opbank = models.IntegerField(null=True,blank=True,default=0)
    clbank = models.IntegerField(null=True,blank=True,default=0)
    bankrec = models.IntegerField(null=True,blank=True,default=0)
    bankpmt = models.IntegerField(null=True,blank=True,default=0)
    opcash = models.IntegerField(null=True,blank=True,default=0)
    clcash = models.IntegerField(null=True,blank=True,default=0)
    cashrec = models.IntegerField(null=True,blank=True,default=0)
    cashpmt = models.IntegerField(null=True,blank=True,default=0)
    acamt = models.IntegerField(null=True,blank=True,default=0)
    hqamt = models.IntegerField(null=True,blank=True,default=0)
    defaultbank = models.CharField(max_length=1,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    #created_at =  models.DateField(auto_now_add=True,auto_now=False,blank=True)
    #updated_at =  models.DateField(auto_now_add=False,auto_now=True,blank=True)
    


    def __str__(self):
        return self.locationname




class Opcltmp(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True)
    bankac = models.CharField(max_length=20,null=True,blank=True)
    bankacname = models.CharField(max_length=50,null=True,blank=True)
    bankname = models.CharField(max_length=50,null=True,blank=True)
    bankcode = models.CharField(max_length=4,null=True,blank=True)
    bankbranch = models.CharField(max_length=100,null=True,blank=True)
    bankifsc = models.CharField(max_length=20,null=True,blank=True)
    opbank = models.IntegerField(null=True,blank=True,default=0)
    clbank = models.IntegerField(null=True,blank=True,default=0)
    bankrec = models.IntegerField(null=True,blank=True,default=0)
    bankpmt = models.IntegerField(null=True,blank=True,default=0)
    opcash = models.IntegerField(null=True,blank=True,default=0)
    clcash = models.IntegerField(null=True,blank=True,default=0)
    cashrec = models.IntegerField(null=True,blank=True,default=0)
    cashpmt = models.IntegerField(null=True,blank=True,default=0)

    def __str__(self):
        return self.locationname




class Userlogged(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    username = models.CharField(max_length=50,null=True,blank=True)
    rundate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
    logindatetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ip = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.username







class Loanmaster(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     transid = models.CharField(max_length=16,null=True,blank=True)
     apptitle = models.CharField(max_length=6,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     appgender = models.CharField(max_length=10,null=True,blank=True)
     appdob = models.DateField(auto_now_add=False,auto_now=False,blank=True)
     appadharno = models.CharField(max_length=12,null=True,blank=True)
     apppanno = models.CharField(max_length=10,null=True,blank=True)
     coappname = models.CharField(max_length=100,null=True,blank=True)
     coapprelation = models.CharField(max_length=100,null=True,blank=True)
     coappdob = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     coappgender = models.CharField(max_length=10,null=True,blank=True)
     coappadharno = models.CharField(max_length=12,null=True,blank=True)
     coapppanno = models.CharField(max_length=10,null=True,blank=True)
     appfathername = models.CharField(max_length=100,null=True,blank=True)
     appmaritalstatus = models.CharField(max_length=25,null=True,blank=True)
     appmobileno = models.CharField(max_length=10,null=True,blank=True)
     coappmobileno = models.CharField(max_length=10,null=True,blank=True)
     appnoofdependent = models.IntegerField(null=True,blank=True,default=0)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddlandmark = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     apppresentaddpin = models.CharField(max_length=6,null=True,blank=True)
     apppermanentadd = models.CharField(max_length=500,null=True,blank=True)
     apppermanentaddcity = models.CharField(max_length=200,null=True,blank=True)
     apppermanentaddpin = models.CharField(max_length=6,null=True,blank=True)
     guarname = models.CharField(max_length=100,null=True,blank=True)
     guardob = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     guargender = models.CharField(max_length=10,null=True,blank=True)
     guarfathername = models.CharField(max_length=100,null=True,blank=True)
     guaradharno = models.CharField(max_length=12,null=True,blank=True)
     guarpanno = models.CharField(max_length=10,null=True,blank=True)
     guarrelation = models.CharField(max_length=50,null=True,blank=True)
     guarpresentadd = models.CharField(max_length=500,null=True,blank=True)
     guarpresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     guarpresentaddpin = models.CharField(max_length=6,null=True,blank=True)
     guaroccupation = models.CharField(max_length=200,null=True,blank=True)
     guaroccupationadd = models.CharField(max_length=500,null=True,blank=True)
     guarmobileno = models.CharField(max_length=10,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)
     appshopadd = models.CharField(max_length=500,null=True,blank=True)
     appshoplocation = models.CharField(max_length=500,null=True,blank=True)
     appshopdetail = models.CharField(max_length=200,null=True,blank=True)
     appdailysale = models.IntegerField(null=True,blank=True,default=0)
     appdailyincome = models.IntegerField(null=True,blank=True,default=0)
     apploanpurpose = models.CharField(max_length=200,null=True,blank=True)
     apploanamt = models.IntegerField(null=True,blank=True,default=0)
     apploanint = models.IntegerField(null=True,blank=True,default=0)
     apploanaddint = models.IntegerField(null=True,blank=True,default=0)
     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploanemi = models.IntegerField(null=True,blank=True,default=0)
     grouploanemi = models.IntegerField(null=True,blank=True,default=0)
     apploanemiprin = models.IntegerField(null=True,blank=True,default=0)
     apploanemiint = models.IntegerField(null=True,blank=True,default=0)
     apploantenr = models.IntegerField(null=True,blank=True,default=0)
     appemifreq= models.CharField(max_length=50,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     appemiduedate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     appemifirstfn = models.CharField(max_length=2, null=True, blank=True)
     appemisecondfn = models.CharField(max_length=2, null=True, blank=True)
     colldaychar= models.CharField(max_length=100,null=True,blank=True)
     colldaynum= models.IntegerField(null=True,blank=True,default=0)
     delaydays1 = models.IntegerField(null=True,blank=True,default=0)
     delaydays2 = models.IntegerField(null=True,blank=True,default=0)
     delaydays3 = models.IntegerField(null=True,blank=True,default=0)
     apploandueamt = models.IntegerField(null=True,blank=True,default=0)
     apploanbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamt = models.IntegerField(null=True,blank=True,default=0)
     appprinrecamt = models.IntegerField(null=True,blank=True,default=0)
     appintrecamt = models.IntegerField(null=True,blank=True,default=0)
     applatefeeamt = models.IntegerField(null=True,blank=True,default=0)
     instdue = models.DecimalField(max_digits=7,decimal_places=2,default=0.0)
     instdone = models.DecimalField(max_digits=7,decimal_places=2,default=0.0)
     instoverdue = models.DecimalField(max_digits=7,decimal_places=2,default=0.0)
     instoverdueamt = models.IntegerField(null=True,blank=True,default=0)
     instoverduetmp = models.DecimalField(max_digits=7,decimal_places=2,default=0.0)
     instoverdueamttmp = models.IntegerField(null=True,blank=True,default=0)
     status = models.CharField(max_length=1,null=True,blank=True)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     appbankac = models.CharField(max_length=100,null=True,blank=True)
     appbankname = models.CharField(max_length=200,null=True,blank=True)
     appbankbranch = models.CharField(max_length=200,null=True,blank=True)
     appbankifsc = models.CharField(max_length=100,null=True,blank=True)
     appnameasbank = models.CharField(max_length=100,null=True,blank=True)
     appchq = models.CharField(max_length=10,null=True,blank=True)
     appnoofchq = models.IntegerField(null=True,blank=True,default=0)
     appchqno1 = models.CharField(max_length=10,null=True,blank=True)
     appchqno2 = models.CharField(max_length=10,null=True,blank=True)
     applifeinsur = models.CharField(max_length=4,null=True,blank=True,default="N")
     applifeinsurdays = models.CharField(max_length=4,null=True,blank=True,default="N")
     applifeinsurdate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applifeinsuruptodate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applifeinsurclaim = models.CharField(max_length=4,null=True,blank=True,default="N")
     appdeathdate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applifeinsurclaimmode = models.CharField(max_length=100,null=True,blank=True,default="N")
     applifeinsurclaimdate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applifeinsurclaimamount = models.IntegerField(null=True,blank=True,default=0)
     writtenoff = models.CharField(max_length=1,null=True,blank=True,default="N")
     writtencode = models.CharField(max_length=2,null=True,blank=True,default="N")
     writtenofamounttotal = models.CharField(max_length=20, null=True, blank=True)
     writtenofamountprin = models.CharField(max_length=20, null=True, blank=True)
     loantype = models.CharField(max_length=50,null=True,blank=True)
     groupid = models.CharField(max_length=8,null=True,blank=True)
     groupleaderloanid = models.CharField(max_length=13,null=True,blank=True)
     groupleadername = models.CharField(max_length=100,null=True,blank=True)
     groupleader = models.CharField(max_length=1,null=True,blank=True)
     rpersoncode = models.CharField(max_length=10,null=True,blank=True)
     rpersonname = models.CharField(max_length=100,null=True,blank=True)
     associatecode = models.CharField(max_length=10,null=True,blank=True)
     associatename = models.CharField(max_length=100,null=True,blank=True)
     adminpersoncode = models.CharField(max_length=10,null=True,blank=True)
     adminpersonname = models.CharField(max_length=100,null=True,blank=True)
     mode = models.CharField(max_length=12,null=True,blank=True)
     disbchq = models.CharField(max_length=16,null=True,blank=True)
     formno = models.CharField(max_length=12,null=True,blank=True)
     passbookno = models.CharField(max_length=12,null=True,blank=True)
     procfeereceipt = models.CharField(max_length=1, null=True, blank=True)
     groupemicoll = models.CharField(max_length=1, null=True, blank=True)
     assoexp = models.CharField(max_length=1, null=True, blank=True)
     assoexpamt = models.IntegerField(null=True,blank=True,default=0)     
     assoexppaydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     assoexppaytransid = models.CharField(max_length=16, null=True, blank=True)
     assoexpstatus = models.CharField(max_length=1, null=True, blank=True)
     duescheme = models.IntegerField(null=True,blank=True,default=0)
     duewithint = models.IntegerField(null=True,blank=True,default=0)
     duewithlate = models.IntegerField(null=True,blank=True,default=0)

     def __str__(self):
         return self.loanid

class Loanlead(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     appmaritalstatus = models.CharField(max_length=25,null=True,blank=True)
     appgender = models.CharField(max_length=10,null=True,blank=True)
     appmobileno = models.CharField(max_length=10,null=True,blank=True)
     appshoplocation = models.CharField(max_length=500,null=True,blank=True)
     appbusiness = models.CharField(max_length=500,null=True,blank=True)
     leaddate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     firemark1 = models.CharField(max_length=500,null=True,blank=True)
     firemark2 = models.CharField(max_length=500,null=True,blank=True)
     fidate1= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     fistatus1 = models.CharField(max_length=1,null=True,blank=True)
     fidate2= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     fistatus2 = models.CharField(max_length=1,null=True,blank=True)
     leadpersoncode = models.CharField(max_length=10,null=True,blank=True)
     leadpersonname = models.CharField(max_length=100,null=True,blank=True)
     secondpersoncode = models.CharField(max_length=10,null=True,blank=True)
     secondpersonname = models.CharField(max_length=100,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)
     loandisb = models.CharField(max_length=1,null=True,blank=True)
     loanmaster = models.ForeignKey(Loanmaster,on_delete=models.CASCADE,default=1)
     tmppersoncode = models.CharField(max_length=10,null=True,blank=True)

     def __str__(self):
         return self.appname


class Loanleadtmp(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     appmaritalstatus = models.CharField(max_length=25,null=True,blank=True)
     appgender = models.CharField(max_length=10,null=True,blank=True)
     appmobileno = models.CharField(max_length=10,null=True,blank=True)
     appshoplocation = models.CharField(max_length=500,null=True,blank=True)
     appbusiness = models.CharField(max_length=500,null=True,blank=True)
     leaddate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     firemark1 = models.CharField(max_length=500,null=True,blank=True)
     firemark2 = models.CharField(max_length=500,null=True,blank=True)
     fidate1= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     fistatus1 = models.CharField(max_length=1,null=True,blank=True)
     fidate2= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     fistatus2 = models.CharField(max_length=1,null=True,blank=True)
     leadpersoncode = models.CharField(max_length=10,null=True,blank=True)
     leadpersonname = models.CharField(max_length=100,null=True,blank=True)
     secondpersoncode = models.CharField(max_length=10,null=True,blank=True)
     secondpersonname = models.CharField(max_length=100,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)
     loandisb = models.CharField(max_length=1,null=True,blank=True)
     loanmaster = models.ForeignKey(Loanmaster,on_delete=models.CASCADE,default=1)
     tmppersoncode = models.CharField(max_length=10,null=True,blank=True)

     def __str__(self):
         return self.appname


class Loanleadsumm(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     personcode = models.CharField(max_length=10, null=True, blank=True)
     personname = models.CharField(max_length=100, null=True, blank=True)
     leads = models.IntegerField(null=True,blank=True,default=0)     
     disb = models.IntegerField(null=True,blank=True,default=0)     
     rejected = models.IntegerField(null=True,blank=True,default=0)     
     active = models.IntegerField(null=True,blank=True,default=0) 
     datarange =  models.CharField(max_length=10, null=True, blank=True)   

     def __str__(self):
         return self.appname


class Loanscheme(models.Model):
    
    loanamt = models.IntegerField(null=True,blank=True,default=0)
    loandays = models.IntegerField(null=True,blank=True,default=0)
    loantenr = models.DecimalField(max_digits=9, decimal_places=2)
    emifreq = models.CharField(max_length=20, null=True, blank=True)
    procfee = models.IntegerField(null=True,blank=True,default=0)
    active = models.CharField(max_length=1,null=True,blank=True)

    
    def __str__(self):
        return self.loanamt


class Rate(models.Model):
    
    days = models.IntegerField(null=True,blank=True,default=0)
    rate = models.DecimalField(max_digits=9, decimal_places=2,default=0.00)  
    date = models.DateField(auto_now_add=False,auto_now=False,null=True)

    def __str__(self):
        return self.rate




class Personmaster(models.Model):
    
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50, null=True, blank=True)
    personcode = models.CharField(max_length=8,null=True,blank=True)
    personname = models.CharField(max_length=100,null=True,blank=True)
    persondesig = models.CharField(max_length=100,null=True,blank=True)
    persontype = models.CharField(max_length=4,null=True,blank=True)
    doj = models.DateField(auto_now_add=False,auto_now=False,null=True)
    dob = models.DateField(auto_now_add=False,auto_now=False,null=True)
    dom = models.DateField(auto_now_add=False,auto_now=False,null=True)
    admin = models.CharField(max_length=1,null=True,blank=True)

        
    def __str__(self):
        return self.loanamt


class Transcd(models.Model):
    
    transcd = models.CharField(unique=True,max_length=4,null=True,blank=True)
    transnm = models.CharField(max_length=100,null=True,blank=True)
    transtype = models.CharField(max_length=10,null=True,blank=True)
    acperm = models.CharField(max_length=1,null=True,blank=True)
    advperm = models.CharField(max_length=1,null=True,blank=True)
    
        
    def __str__(self):
        return self.transnm


class Daybook(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     loanid = models.CharField(max_length=16,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     narration = models.CharField(max_length=200,null=True,blank=True)
     remark = models.CharField(max_length=200,null=True,blank=True)
     amount = models.IntegerField(null=True,blank=True,default=0)
     drcr = models.CharField(max_length=1,null=True,blank=True)
     trans = models.ForeignKey(Transcd,on_delete=models.CASCADE)
     clcashbank = models.ForeignKey(Opclcashbank,on_delete=models.CASCADE)

     def __str__(self):
         return self.locationcode


class Advancesmaster(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     remark = models.CharField(max_length=200,null=True,blank=True)
     dramount = models.IntegerField(null=True,blank=True,default=0)
     cramount = models.IntegerField(null=True,blank=True,default=0)
     balamount = models.IntegerField(null=True,blank=True,default=0)
     settlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)

     def __str__(self):
         return self.locationcode

class Advancestrans(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     advanceid = models.CharField(max_length=16,null=True,blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     amount = models.IntegerField(null=True,blank=True,default=0)
     drcr = models.CharField(max_length=1,null=True,blank=True)
     master = models.ForeignKey(Advancesmaster,on_delete=models.CASCADE)

     def __str__(self):
         return self.locationcode


class Generalloanmaster(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     remark = models.CharField(max_length=200,null=True,blank=True)
     dramount = models.IntegerField(null=True,blank=True,default=0)
     cramount = models.IntegerField(null=True,blank=True,default=0)
     balamount = models.IntegerField(null=True,blank=True,default=0)
     settlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)

     def __str__(self):
         return self.locationcode

class Generalloantrans(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(max_length=16,null=True,blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     amount = models.IntegerField(null=True,blank=True,default=0)
     drcr = models.CharField(max_length=1,null=True,blank=True)
     master = models.ForeignKey(Advancesmaster,on_delete=models.CASCADE)

     def __str__(self):
         return self.locationcode


class Authcenterexpance(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50,null=True,blank=True)
     personcode = models.CharField(max_length=8, null=True, blank=True)
     personname = models.CharField(max_length=100, null=True, blank=True)
     fromdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     todate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     transcd = models.CharField(max_length=4, null=True, blank=True)
     transnm = models.CharField(max_length=100, null=True, blank=True)
     totalamount = models.IntegerField(null=True, blank=True, default=0)
     date= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     transid = models.CharField(max_length=16, null=True, blank=True)
     mode = models.CharField(max_length=10, null=True, blank=True)
     amount = models.IntegerField(null=True, blank=True, default=0)
     hqamount = models.IntegerField(null=True, blank=True, default=0)
     paid = models.CharField(max_length=1, null=True, blank=True, default='N')
     hqpaid = models.CharField(max_length=1, null=True, blank=True, default='N')
     hqtransid = models.CharField(max_length=16, null=True, blank=True)
     hqdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)



     def __str__(self):
         return self.locationcode


class Permkey(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50,null=True,blank=True)
     permkey = models.CharField(max_length=16,null=True,blank=True)
     permkeydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     amount = models.IntegerField(null=True,blank=True,default=0)
     personcode = models.CharField(max_length=8,null=True,blank=True)
     personname = models.CharField(max_length=100,null=True,blank=True)
     paydate = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)

     def __str__(self):
         return self.locationcode


class Loantrans(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50,null=True,blank=True)
     transid = models.CharField(max_length=16, null=True, blank=True)
     loanid = models.CharField(max_length=13,null=True,blank=True)
     duedate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     delaydays = models.IntegerField(null=True,blank=True,default=0)     
     mode = models.CharField(max_length=10,null=True,blank=True)
     instno = models.IntegerField(null=True,blank=True,default=0)     
     amount = models.IntegerField(null=True,blank=True,default=0)     
     prinamt = models.IntegerField(null=True,blank=True,default=0)     
     intamt = models.IntegerField(null=True,blank=True,default=0)     
     latefee = models.IntegerField(null=True,blank=True,default=0)     
     drcr = models.CharField(max_length=1,null=True,blank=True)
     master = models.ForeignKey(Loanmaster,on_delete=models.CASCADE)
     flag = models.CharField(max_length=1, null=True, blank=True)

     def __str__(self):
         return self.locationcode


class Emicolldata(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=100,null=True,blank=True)
    loanid = models.CharField(max_length=13,null=True,blank=True)
    groupid = models.CharField(max_length=8,null=True,blank=True)
    appname = models.CharField(max_length=100,null=True,blank=True)
    apploanemi = models.IntegerField(null=True, blank=True, default=0)
    amount = models.IntegerField(null=True,blank=True,default=0)
    latefee = models.IntegerField(null=True,blank=True,default=0)
    lastemidepdate = models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    emiduedate = models.DateTimeField(auto_now_add=False,auto_now=False,blank=True)
    delaydays =  models.IntegerField(null=True,blank=True,default=0)
    delayamount =  models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    processdate =  models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    rundate =  models.DateField(auto_now_add=False,auto_now=False,blank=True)
    status = models.CharField(max_length=1,null=True,blank=True)
    modified = models.CharField(max_length=1,null=True,blank=True) 
    rpersoncode = models.CharField(max_length=10,null=True,blank=True)
    rpersonname = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    master = models.ForeignKey(Loanmaster,on_delete=models.CASCADE)

    def __str__(self):
        return self.locationname

class Emisundry(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=100,null=True,blank=True)
    transid = models.CharField(max_length=16, null=True, blank=True)
    loanid = models.CharField(max_length=13,null=True,blank=True)
    appname = models.CharField(max_length=100,null=True,blank=True)
    apploanemi = models.IntegerField(null=True, blank=True, default=0)
    amount = models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    transdate =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    processdate =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    processtransid = models.CharField(max_length=16, null=True, blank=True)
    mode = models.CharField(max_length=10,null=True,blank=True)
    status = models.CharField(max_length=1,null=True,blank=True)


    def __str__(self):
        return self.locationname

class Groupemicolldata(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=100,null=True,blank=True)
    loanid = models.CharField(max_length=13, null=True, blank=True)
    groupid = models.CharField(max_length=8,null=True,blank=True)
    groupleaderloanid = models.CharField(max_length=13,null=True,blank=True)
    groupleadername = models.CharField(max_length=100,null=True,blank=True)
    appname = models.CharField(max_length=100,null=True,blank=True)
    apploanemi = models.IntegerField(null=True, blank=True, default=0)
    amount = models.IntegerField(null=True,blank=True,default=0)
    latefee = models.IntegerField(null=True,blank=True,default=0)
    lastemidepdate = models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    emiduedate = models.DateTimeField(auto_now_add=False,auto_now=False,blank=True)
    delaydays =  models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    processdate =  models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)
    rundate =  models.DateField(auto_now_add=False,auto_now=False,blank=True)
    status = models.CharField(max_length=1,null=True,blank=True)
    modified = models.CharField(max_length=1,null=True,blank=True) 
    rpersoncode = models.CharField(max_length=10,null=True,blank=True)
    rpersonname = models.CharField(max_length=100,null=True,blank=True)
    master = models.ForeignKey(Loanmaster,on_delete=models.CASCADE)

    def __str__(self):
        return self.locationname


class Fundmaster(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    transid = models.CharField(max_length=16,null=True,blank=True)
    personcode = models.CharField(max_length=8,null=True,blank=True)
    personname = models.CharField(max_length=100,null=True,blank=True)
    persondesig = models.CharField(max_length=100,null=True,blank=True)
    persontype = models.CharField(max_length=3,null=True,blank=True)
    relatedpersonname = models.CharField(max_length=100,null=True,blank=True)
    transcd = models.CharField(max_length=4,null=True,blank=True)
    transnm = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=10,null=True,blank=True)
    bankac = models.CharField(max_length=20,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    drcr = models.CharField(max_length=1,null=True,blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    mis = models.CharField(max_length=1, null=True, blank=True)
    misamount =  models.IntegerField(null=True,blank=True,default=0)
    inttype = models.CharField(max_length=10, null=True, blank=True)
    intrate = models.DecimalField(max_digits=9, decimal_places=2,default=0.00)
    intpaymode = models.CharField(max_length=20, null=True, blank=True)
    intduedate = models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    lastintpaydate = models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    intrestamount = models.IntegerField(null=True,blank=True,default=0)
    mispaid =  models.IntegerField(null=True,blank=True,default=0)
    remarks = models.CharField(max_length=20, null=True, blank=True)
    
    
    def __str__(self):
        return self.personname


class Fundmasteroth(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    transid = models.CharField(max_length=16,null=True,blank=True)
    personcode = models.CharField(max_length=8,null=True,blank=True)
    personname = models.CharField(max_length=100,null=True,blank=True)
    persondesig = models.CharField(max_length=100,null=True,blank=True)
    persontype = models.CharField(max_length=4,null=True,blank=True)
    transcd = models.CharField(max_length=4,null=True,blank=True)
    transnm = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=10,null=True,blank=True)
    bankac = models.CharField(max_length=20,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    drcr = models.CharField(max_length=1,null=True,blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    
    
    def __str__(self):
        return self.personname


class Fundtrans(models.Model):
    locationcode = models.CharField(max_length=4,null=True,blank=True)
    locationname = models.CharField(max_length=50,null=True,blank=True)
    fundid = models.CharField(max_length=16,null=True,blank=True)
    transid = models.CharField(max_length=16,null=True,blank=True)
    personcode = models.CharField(max_length=8,null=True,blank=True)
    personname = models.CharField(max_length=100,null=True,blank=True)
    transcd = models.CharField(max_length=4,null=True,blank=True)
    transnm = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=10,null=True,blank=True)
    bankac = models.CharField(max_length=20,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True,default=0)
    date =  models.DateField(auto_now_add=False,auto_now=False,blank=True,null=True)
    drcr = models.CharField(max_length=1,null=True,blank=True)
    fundmast = models.ForeignKey(Fundmaster, on_delete=models.CASCADE)
 
    def __str__(self):
        return self.loanamt




class Gstdata(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     appfathername = models.CharField(max_length=100,null=True,blank=True)
     apploandate = models.DateField(auto_now_add=False,auto_now=False,blank=True)
     apploanamt = models.IntegerField(null=True,blank=True,default=0)
     processingfee = models.IntegerField(null=True,blank=True,default=0)
     gstamount = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
     fromdate= models.DateField(auto_now_add=False,auto_now=False,blank=True)
     todate= models.DateField(auto_now_add=False,auto_now=False,blank=True)

     def __str__(self):
         return self.locationcode


class Crifdata(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     appname = models.CharField(max_length=100, null=True, blank=True)
     firstname = models.CharField(max_length=100, null=True, blank=True)
     middlename = models.CharField(max_length=100, null=True, blank=True)
     lastname = models.CharField(max_length=100, null=True, blank=True)
     dobddmmyyyy = models.CharField(max_length=8, null=True, blank=True)
     gender = models.CharField(max_length=10, null=True, blank=True)
     panno = models.CharField(max_length=10, null=True, blank=True)
     passportno = models.CharField(max_length=20, null=True, blank=True)
     voteridno = models.CharField(max_length=20, null=True, blank=True)
     dlno = models.CharField(max_length=20, null=True, blank=True)
     rationcardno = models.CharField(max_length=20, null=True, blank=True)
     uid = models.CharField(max_length=12,null=True,blank=True)
     aid = models.CharField(max_length=12,null=True,blank=True)
     telephoneno1 = models.CharField(max_length=10, null=True, blank=True)
     telephonetype1 = models.CharField(max_length=2, null=True, blank=True)
     telephoneno2 = models.CharField(max_length=10, null=True, blank=True)
     telephonetype2 = models.CharField(max_length=2, null=True, blank=True)
     telephoneno3 = models.CharField(max_length=10, null=True, blank=True)
     telephonetype3 = models.CharField(max_length=2, null=True, blank=True)
     telephoneext = models.CharField(max_length=10, null=True, blank=True)
     emailid = models.CharField(max_length=50, null=True, blank=True)
     consumeradd1 = models.CharField(max_length=200, null=True, blank=True)
     consumercity1 = models.CharField(max_length=100, null=True, blank=True)
     consumerdistrict1 = models.CharField(max_length=100, null=True, blank=True)
     consumerstatecode1 = models.CharField(max_length=2, null=True, blank=True)
     consumerpincode1 = models.CharField(max_length=6, null=True, blank=True)
     consumeraddcategory1 = models.CharField(max_length=2, null=True, blank=True)
     consumerresicode1 = models.CharField(max_length=2, null=True, blank=True)
     consumeradd2 = models.CharField(max_length=200, null=True, blank=True)
     consumercity2 = models.CharField(max_length=100, null=True, blank=True)
     consumerdistrict2 = models.CharField(max_length=100, null=True, blank=True)
     consumerstatecode2 = models.CharField(max_length=2, null=True, blank=True)
     consumerpincode2 = models.CharField(max_length=6, null=True, blank=True)
     consumeraddcategory2 = models.CharField(max_length=2, null=True, blank=True)
     consumerresicode2 = models.CharField(max_length=2, null=True, blank=True)
     membercode = models.CharField(max_length=13,null=True,blank=True)
     membershortname = models.CharField(max_length=100, null=True, blank=True)
     loanacno = models.CharField(max_length=13, null=True, blank=True)
     acnotype = models.CharField(max_length=2, null=True, blank=True)
     ownershipindi = models.CharField(max_length=1, null=True, blank=True)
     loandtddmmyyyy = models.CharField(max_length=8, null=True, blank=True)
     lastemiddmmyyyy = models.CharField(max_length=8, null=True, blank=True)
     closedtddmmyyyy = models.CharField(max_length=8, null=True, blank=True)
     reportdateddmmyyyy = models.CharField(max_length=8, null=True, blank=True)
     loanamount = models.CharField(max_length=8, null=True, blank=True)
     curruntbalance = models.CharField(max_length=20, null=True, blank=True)
     amountoverdue = models.CharField(max_length=8, null=True, blank=True)
     numberofdayspast = models.CharField(max_length=8, null=True, blank=True)
     oldmembercode = models.CharField(max_length=13, null=True, blank=True)
     oldmembershortname = models.CharField(max_length=100, null=True, blank=True)
     oldloanacno = models.CharField(max_length=13, null=True, blank=True)
     oldacnotype = models.CharField(max_length=2, null=True, blank=True)
     oldownershipindi = models.CharField(max_length=1, null=True, blank=True)
     suitfiled = models.CharField(max_length=100, null=True, blank=True)
     writtenoff = models.CharField(max_length=100, null=True, blank=True)
     assetclassification = models.CharField(max_length=2, null=True, blank=True)
     valueofcollateral = models.CharField(max_length=20, null=True, blank=True)
     typeofcollateral = models.CharField(max_length=20, null=True, blank=True)
     creditlimit = models.CharField(max_length=20, null=True, blank=True)
     cashlimit = models.CharField(max_length=20, null=True, blank=True)
     roi = models.CharField(max_length=20, null=True, blank=True)
     repaymenttenure = models.CharField(max_length=20, null=True, blank=True)
     emiamount = models.CharField(max_length=20, null=True, blank=True)
     writtenofamounttotal = models.CharField(max_length=20, null=True, blank=True)
     writtenofamountprin = models.CharField(max_length=20, null=True, blank=True)
     settlementamount = models.CharField(max_length=20, null=True, blank=True)
     paymentgrequency = models.CharField(max_length=20, null=True, blank=True)
     actualpaymentamount = models.CharField(max_length=20, null=True, blank=True)
     occupationcode = models.CharField(max_length=20, null=True, blank=True)
     income = models.CharField(max_length=20, null=True, blank=True)
     netincomeindicator = models.CharField(max_length=20, null=True, blank=True)
     monthlyincomeindicator = models.CharField(max_length=20, null=True, blank=True)


     def __str__(self):
         return self.loanid



class Licdata(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(max_length=13, null=True, blank=True)
     appname = models.CharField(max_length=100, null=True, blank=True)
     appgender = models.CharField(max_length=10,null=True,blank=True)
     appdob = models.DateField(auto_now_add=False,auto_now=False,blank=True)
     dobdtddmmyyyy = models.CharField(max_length=10, null=True, blank=True)
     coappname = models.CharField(max_length=100,null=True,blank=True)
     coappdob = models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     coappdobddmmyyyy = models.CharField(max_length=10, null=True, blank=True)
     loandate = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True)
     loandtddmmyyyy = models.CharField(max_length=10, null=True, blank=True)
     loantype = models.CharField(max_length=20, null=True, blank=True)
     loanamount = models.CharField(max_length=8, null=True, blank=True)
     balamount = models.CharField(max_length=8, null=True, blank=True)
     loantenr = models.IntegerField(null=True,blank=True,default=0)
     insurdays = models.IntegerField(null=True,blank=True,default=0)
     premium = models.IntegerField(null=True,blank=True,default=0)
     gst = models.IntegerField(null=True,blank=True,default=0)
     total = models.IntegerField(null=True, blank=True, default=0)
     lastinsurupto = models.DateField(auto_now_add=False, auto_now=False, blank=True)
     lastinsuruptodtddmmyyyy = models.CharField(
         max_length=10, null=True, blank=True)
     dor = models.DateField(auto_now_add=False, auto_now=False, blank=True)
     dordtddmmyyyy = models.CharField(max_length=10, null=True, blank=True)
     loanstatus = models.CharField(max_length=20, null=True, blank=True)


     def __str__(self):
         return self.loanid



class Auditloanmaster20252026(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)

     appprindueamt = models.IntegerField(null=True, blank=True, default=0)
     appintdueamt = models.IntegerField(null=True, blank=True, default=0)
     apptotaldueamt = models.IntegerField(null=True, blank=True, default=0)

     appdueamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20242025 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20252026 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20252026 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20252026 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20252026 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt = models.IntegerField(null=True, blank=True, default=0)

     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     #apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     #apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode




class Auditloanmaster20242025(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)

     appprindueamt = models.IntegerField(null=True, blank=True, default=0)
     appintdueamt = models.IntegerField(null=True, blank=True, default=0)
     apptotaldueamt = models.IntegerField(null=True, blank=True, default=0)

     appdueamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20242025 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20242025 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt = models.IntegerField(null=True, blank=True, default=0)

     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     #apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     #apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode


class Auditloanmaster20232024(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)

     appprindueamt = models.IntegerField(null=True, blank=True, default=0)
     appintdueamt = models.IntegerField(null=True, blank=True, default=0)
     apptotaldueamt = models.IntegerField(null=True, blank=True, default=0)

     appdueamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20232024 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20232024 = models.IntegerField(null=True, blank=True, default=0)


     appprinrecamt = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt = models.IntegerField(null=True, blank=True, default=0)

     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     #apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     #apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode



class Auditloanmaster20222023(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)

     appprindueamt = models.IntegerField(null=True, blank=True, default=0)
     appintdueamt = models.IntegerField(null=True, blank=True, default=0)
     apptotaldueamt = models.IntegerField(null=True, blank=True, default=0)

     appdueamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20222023 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20222023 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt = models.IntegerField(null=True, blank=True, default=0)

     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     #apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     #apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode





class Auditloanmaster20212022(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)

     appprindueamt = models.IntegerField(null=True, blank=True, default=0)
     appintdueamt = models.IntegerField(null=True, blank=True, default=0)
     apptotaldueamt = models.IntegerField(null=True, blank=True, default=0)

     appdueamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appdueamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt20212022 = models.IntegerField(null=True, blank=True, default=0)

     appprinrecamt = models.IntegerField(null=True, blank=True, default=0)
     appintrecamt = models.IntegerField(null=True, blank=True, default=0)
     apptotalrecamt = models.IntegerField(null=True, blank=True, default=0)

     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     #apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     #apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode



class Auditloanmaster20202021(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     apppresentadd = models.CharField(max_length=500,null=True,blank=True)
     apppresentaddcity = models.CharField(max_length=200,null=True,blank=True)
     appoccupation = models.CharField(max_length=200,null=True,blank=True)
     appshoplocation = models.CharField(max_length=500,null=True,blank=True)

     appprinbalamt20192020 = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt20192020 = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt20192020 = models.IntegerField(null=True,blank=True,default=0)
     
     apploanamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     apploanint20202021 = models.IntegerField(null=True,blank=True,default=0)
     apploandueamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     
     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)     

     appprinrecamt20192020 = models.IntegerField(null=True,blank=True,default=0)
     appintrecamt20192020 = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamt20192020 = models.IntegerField(null=True,blank=True,default=0)

     appprinrecamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     appintrecamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamt20202021 = models.IntegerField(null=True,blank=True,default=0)

     appprinrecamt = models.IntegerField(null=True,blank=True,default=0)
     appintrecamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamt = models.IntegerField(null=True,blank=True,default=0)

     apptotalrecamtcash = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamtbank = models.IntegerField(null=True,blank=True,default=0)

     appprinbalamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt20202021 = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt20202021 = models.IntegerField(null=True,blank=True,default=0)

     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploansettlementdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)
     status = models.CharField(max_length=1,null=True,blank=True)


     def __str__(self):
         return self.locationcode

class Auditloanrecov20192020(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     loanid = models.CharField(unique=True,max_length=13,null=True,blank=True)
     apploandate= models.DateField(auto_now_add=False,auto_now=False)
     apploanamt = models.IntegerField(null=True,blank=True,default=0)
     apploanint = models.IntegerField(null=True,blank=True,default=0)
     apploandueamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalrecamt = models.IntegerField(null=True,blank=True,default=0)
     appprinrecamt = models.IntegerField(null=True,blank=True,default=0)
     appintrecamt = models.IntegerField(null=True,blank=True,default=0)
     apptotalbalamt = models.IntegerField(null=True,blank=True,default=0)
     appprinbalamt = models.IntegerField(null=True,blank=True,default=0)
     appintbalamt = models.IntegerField(null=True,blank=True,default=0)
     applastemidepdate= models.DateField(auto_now_add=False,auto_now=False,null=True,blank=True)

     def __str__(self):
         return self.locationcode



class Daydrcr(models.Model):
     locationcode = models.CharField(max_length=4,null=True,blank=True)
     locationname = models.CharField(max_length=50, null=True, blank=True)
     date= models.DateField(auto_now_add=False,auto_now=False)
     transid = models.CharField(max_length=16,null=True,blank=True)
     transcd = models.CharField(max_length=4,null=True,blank=True)
     transnm = models.CharField(max_length=100,null=True,blank=True)
     mode = models.CharField(max_length=10,null=True,blank=True)
     chequeno = models.CharField(max_length=50,null=True,blank=True)
     bankac = models.CharField(max_length=50,null=True,blank=True)
     loanid = models.CharField(max_length=14,null=True,blank=True)
     appname = models.CharField(max_length=100,null=True,blank=True)
     narration = models.CharField(max_length=200,null=True,blank=True)
     remark = models.CharField(max_length=200,null=True,blank=True)
     amount = models.IntegerField(null=True,blank=True,default=0)
     drcr = models.CharField(max_length=1,null=True,blank=True)

     def __str__(self):
         return self.locationcode



class Fundsendreceive(models.Model):
    locationcode = models.CharField(max_length=4, null=True, blank=True)
    locationname = models.CharField(max_length=50, null=True, blank=True)
    fromdate = models.DateField(auto_now_add=False, auto_now=False, blank=True,default='2020-01-01')
    todate = models.DateField(
        auto_now_add=False, auto_now=False, blank=True, default='2020-01-01')
    transid = models.CharField(max_length=16, null=True, blank=True)
    transtransid = models.CharField(max_length=16, null=True, blank=True)
    translocationcode = models.CharField(max_length=4, null=True, blank=True)
    translocationname = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    transdate = models.DateField(
        auto_now_add=False, auto_now=False, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True, default=0)
    fundtype = models.CharField(max_length=100, null=True, blank=True)
    mode = models.CharField(max_length=10, null=True, blank=True)
    transcd = models.CharField(max_length=4, null=True, blank=True)
    transnm = models.CharField(max_length=100, null=True, blank=True)
    drcr = models.CharField(max_length=1, null=True, blank=True)
    status = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return self.locationcode

     
class Insurancebooking(models.Model):

     booking_Date = models.DateField(auto_now_add=False,auto_now=False)
     Leadid = models.CharField(max_length=14,null=True,blank=True)
     Insured_name = models.CharField(max_length=50,null=True,blank=True)
     Dob = models.DateField(auto_now_add=False,auto_now=False)
     Insurer =  models.CharField(max_length=100,null=True,blank=True)
     Product = models.CharField(max_length=100,null=True,blank=True)
     Plan_name = models.CharField(max_length=100,null=True,blank=True)
     Sum_insured = models.CharField(max_length=14,null=True,blank=True)
     Basic_premium = models.CharField(max_length=14,null=True,blank=True)
     Net_premium = models.CharField(max_length=14,null=True,blank=True)
     Premium = models.CharField(max_length=14,null=True,blank=True)
     Od_Premium = models.CharField(max_length=14,null=True,blank=True)
     Ape = models.CharField(max_length=14,null=True,blank=True)
     Status = models.CharField(max_length=14,null=True,blank=True)
     City = models.CharField(max_length=14,null=True,blank=True)
     Applicationno = models.CharField(max_length=14,null=True,blank=True)
     Policyno =  models.CharField(max_length=14,null=True,blank=True)
     Policy_type = models.CharField(max_length=14,null=True,blank=True)
     Payment_periodicity = models.CharField(max_length=14,null=True,blank=True)
     Ise2e = models.CharField(max_length=14,null=True,blank=True)
     Pg_type =  models.CharField(max_length=14,null=True,blank=True)
     Customer_id = models.CharField(max_length=14,null=True,blank=True)
     Address = models.CharField(max_length=100,null=True,blank=True)
     State = models.CharField(max_length=100,null=True,blank=True)
     Pin_code = models.CharField(max_length=100,null=True,blank=True)
     Actual_lead_source = models.CharField(max_length=100,null=True,blank=True)
     Utm_source = models.CharField(max_length=100,null=True,blank=True)
     Utm_term = models.CharField(max_length=20,null=True,blank=True)
     Utm_medium = models.CharField(max_length=20,null=True,blank=True)
     Utm_campaign = models.CharField(max_length=20,null=True,blank=True)
     rm_code = models.CharField(max_length=20,null=True,blank=True)
     rm_name = models.CharField(max_length=20,null=True,blank=True)
     circle = models.CharField(max_length=20,null=True,blank=True)
     lead_rank = models.CharField(max_length=20,null=True,blank=True)
     parentid = models.CharField(max_length=20,null=True,blank=True)
     parent_lead_creation_date = models.DateField(auto_now_add=False,auto_now=False)
     parent_lead_source = models.CharField(max_length=50,null=True,blank=True)
     marital_status = models.CharField(max_length=20,null=True,blank=True)
     lead_date = models.DateField(auto_now_add=False,auto_now=False)
     chat_status = models.CharField(max_length=20,null=True,blank=True)
     issuance_rej_date = models.DateField(auto_now_add=False,auto_now=False)
     payment_substatus = models.CharField(max_length=20,null=True,blank=True)
     installments_paid = models.CharField(max_length=20,null=True,blank=True)
     source = models.CharField(max_length=20,null=True,blank=True)
     partner_filepath_id =  models.CharField(max_length=20,null=True,blank=True)
     vehicle_model_name = models.CharField(max_length=20,null=True,blank=True)
     registration_number = models.CharField(max_length=20,null=True,blank=True)
     registartion_date = models.DateField(auto_now_add=False,auto_now=False)
     isstp = models.CharField(max_length=20,null=True,blank=True)
     fuel_type = models.CharField(max_length=20,null=True,blank=True)
     gvw = models.CharField(max_length=20,null=True,blank=True)
     vechicle_make = models.CharField(max_length=50,null=True,blank=True)
     vehicle_sub_class =  models.CharField(max_length=20,null=True,blank=True)
     vehicleage = models.CharField(max_length=20,null=True,blank=True)
     booking_mode = models.CharField(max_length=20,null=True,blank=True)
     vehicle_carrier = models.CharField(max_length=20,null=True,blank=True)
     noofwheels = models.CharField(max_length=20,null=True,blank=True)
     business_type = models.CharField(max_length=20,null=True,blank=True)
     cc_cubic_capicity = models.CharField(max_length=20,null=True,blank=True)
     kali_peeli = models.CharField(max_length=20,null=True,blank=True)
     cpa_value = models.CharField(max_length=20,null=True,blank=True)
     Stp_nstp = models.CharField(max_length=20,null=True,blank=True)
     no_of_seats = models.CharField(max_length=20,null=True,blank=True)
     Discount = models.CharField(max_length=20,null=True,blank=True)
     tp_premium =  models.CharField(max_length=20,null=True,blank=True) 

     def __str__(self):
        return self.registration_number




class Insurancemaster(models.Model):

     registration_number = models.CharField(max_length=20,null=True,blank=True)
     vehicle_type = models.CharField(max_length=100,null=True,blank=True) 
     vechicle_make = models.CharField(max_length=50,null=True,blank=True)
     vehicle_model_name = models.CharField(max_length=50,null=True,blank=True)
     registrationdate = models.DateField(auto_now_add=True,auto_now=False)
     Owner_name = models.CharField(max_length=100,null=True,blank=True)
     address = models.CharField(max_length=200,null=True,blank=True)
     city = models.CharField(max_length=100,null=True,blank=True)
     mobileno = models.CharField(max_length=10,null=True,blank=True)
     lastinsurer = models.CharField(max_length=100,null=True,blank=True)
     expiredate = models.DateField(auto_now_add=True,auto_now=False)
     date = models.DateField(auto_now_add=True,auto_now=False)


     def __str__(self):
         return self.registration_number