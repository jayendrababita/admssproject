from admssapp.models import Loanmaster, Loanscheme, Personmaster
from admssapp.models import Locationlogin, Daybook, Loantrans, Rate
from datetime import datetime
from datetime import timedelta

from django.db.models import Sum,Count,Case,When,FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import RawSQL
from django.db.models import Q



def updateamount(fapploanid, loginlocationcode, loginrundate):



    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)
    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

    fappname = loanmast.appname
    fapploanid = loanmast.loanid
    fapploanamt = loanmast.apploanamt
    fapploandate = loanmast.apploandate
    fapploanemi = loanmast.apploanemi
    fapploantenr = loanmast.apploantenr
    fapploantype = loanmast.loantype
    fappemifreq = loanmast.appemifreq



    amount = int(fapploanamt)
    ndays = int(fapploantenr)

    ndays = (loginrundate-fapploandate).days

    if ndays <= 90:
        ndays = 90

    if ndays > 90 and ndays <= 180:
        ndays = 180

    if ndays > 180 and ndays <= 270:
        ndays = 270

    if ndays > 270:
        ndays = 334


    rate = Rate.objects.get(days=ndays)
    frate = rate.rate

    if fapploantype == "GROUP":
        rate = Rate.objects.get(days=360 , date='2021-10-19')
        nint=(amount*(frate))/100
        fint=(nint*ndays)/360

    elif  fapploantype == "INDIVIDUAL":
        rate = Rate.objects.get(days=365 , date='2021-10-20')
        frate = rate.rate
        nint=(amount*(frate))/100
        fint=(nint*ndays)/180


    total = amount+fint
    daycoll = round((total/ndays),2)
    weekcoll = round((daycoll*7),2)
    fortnightcoll = round((daycoll*15),2)
    monthcoll = round((daycoll*30),2)

    fapploanint = fint

    if fappemifreq == "WEEKLY":
        fapploanemi = round(weekcoll)
        fapploanemiprin = round((amount/ndays)*7)
        fapploanemiint = fapploanemi-round(fapploanemiprin)
        fappemiduedate = loginrundate + timedelta(7)

    if fappemifreq == "DAILY":
        fapploanemi = round(daycoll)
        fapploanemiprin = round((amount/ndays)*1)
        fapploanemiint = fapploanemi-round(fapploanemiprin)
        fappemiduedate = loginrundate + timedelta(1)

    if fappemifreq == "FORTNIGHTLY":
        fapploanemi = round(fortnightcoll)
        fapploanemiprin = round((amount/ndays)*15)
        fapploanemiint = fapploanemi-round(fapploanemiprin)
        fappemiduedate = loginrundate + timedelta(20)
        if int(loginrundate.strftime("%d")) <= 15:
            fappemiduedate = (fappemiduedate.strftime("%Y"))+(fappemiduedate.strftime("%m"))+'20'
            fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
        elif int(loginrundate.strftime("%d")) >= 16: 
            #later = now + datetime.timedelta(months=1)
            fappemiduedate = (fappemiduedate.strftime("%Y"))+(fappemiduedate.strftime("%m"))+'05'
            fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')

    if fappemifreq == "MONTHLY":
        fapploanemi = round(monthcoll)
        fapploanemiprin = round((amount/ndays)*30)
        fapploanemiint = fapploanemi-round(fapploanemiprin)
        fappemiduedate = loginrundate + timedelta(32)

    print(fapploanamt,fapploanemiprin,fapploanemiint,fapploanint)

    return(fapploanemi, fapploanemiprin, fapploanemiint,fapploanint)
