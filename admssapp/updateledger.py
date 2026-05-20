from admssapp.models import Loanmaster, Loanscheme, Personmaster
from admssapp.models import Locationlogin, Daybook, Loantrans
from datetime import datetime
from datetime import timedelta
from django.db.models.functions import Coalesce
from django.db.models import Sum,Count,Case,When,FloatField


def update(fapploanid, loginlocationcode, loginrundate):


    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)
    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

    loanleddep = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).values('locationcode','loanid').aggregate(noofentry=Coalesce(Count('loanid'),0),totdep=Coalesce(Sum('amount'),0),prindep=Coalesce(Sum('prinamt'),0),intdep=Coalesce(Sum('intamt'),0),latefee=Coalesce(Sum('latefee'),0))
    totdep = loanleddep.get("totdep")
    prindep = loanleddep.get("prindep")
    intdep = loanleddep.get("intdep")
    latefee = loanleddep.get("latefee")

    loanmast.apptotalrecamt = totdep
    loanmast.appprinrecamt =  prindep
    loanmast.appintrecamt = intdep
    loanmast.applatefeeamt = latefee
    loanmast.save()
    

    if loanmast.appemifreq == 'DAILY':
        emifreqdays = 1
    elif loanmast.appemifreq == 'WEEKLY':
        emifreqdays = 7
    elif loanmast.appemifreq == 'FORTNIGHTLY':
        emifreqdays = 15
    elif loanmast.appemifreq == 'MONTHLY':
        emifreqdays = 30

    prevemidate = loanmast.apploandate
    totaldelaydays = 0
    fdepamt = 0
    fcaldepamt = 0
    fcaldepdate = 0


    for a in loanled:
        ######## Extra Intrest ########
        fdepamt = fdepamt + a.amount

        if (a.date - loanmast.apploandate).days <= loanmast.apploantenr:
            fcaldepdate = a.date
            fcaldepamt = fcaldepamt + a.amount

                                 
        flastdepdate = a.date 
        
        ######## Extra Intrest ########
        
        fdelaydays = 0
        noemi = int((a.amount)/loanmast.apploanemi)
        #print(prevemidate, a.date,(a.date - prevemidate).days, emifreqdays*noemi)
        if noemi < 1:
            noemi = 1


        if (a.date - prevemidate).days > emifreqdays*noemi:
            fdelaydays = (a.date - prevemidate).days - emifreqdays*noemi

            #if (a.date - loanmast.apploandate).days > loanmast.apploantenr:
            #    fdelaydays = 0
            
            if fdelaydays < 0:
                fdelaydays = 0
                
            if fdelaydays > 0:
                totaldelaydays = totaldelaydays + fdelaydays
        

        a.duedate = prevemidate+timedelta(days=emifreqdays*noemi)
        a.delaydays = fdelaydays
        prevemidate = a.date
        #week1day = a.date - timedelta(days=a.date.weekday())
        #prevemidate = week1day + timedelta(days=loanmast.colldaynum - 1)
        a.save()
        #print(a.date, a.duedate, a.delaydays, loanmast.colldaynum)
  
  
    loanledtmp = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('-date')
    if loanledtmp:
        noemi = int((loanledtmp[0].amount)/loanmast.apploanemi)
        if noemi < 1:
            noemi = 1

        week1day = loanledtmp[0].date - timedelta(days=a.date.weekday())
        prevemidate = week1day + timedelta(days=loanmast.colldaynum - 1)

        fappemiduedate = prevemidate + timedelta(days=emifreqdays*noemi)
        #fappemiduedate = loanledtmp[0].date + timedelta(days=emifreqdays*noemi)
        fdelaydays = (loginrundate - fappemiduedate).days
    

    else:
        fappemiduedate = loanmast.apploandate + timedelta(days=emifreqdays)
        fdelaydays = (loginrundate - prevemidate).days
        if fdelaydays < 0:
            fdelaydays = 0
        
    
    #fdelaydays = (loginrundate - prevemidate).days

    if fdelaydays < 0:
        fdelaydays = 0

    

    latefee = int((loanmast.apploanamt/1000) * fdelaydays)

    return(fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays)
