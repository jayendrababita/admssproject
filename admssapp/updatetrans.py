from admssapp.models import Loanmaster, Loanscheme, Personmaster
from admssapp.models import Locationlogin, Daybook, Loantrans, Rate
from datetime import datetime
from datetime import timedelta

from django.db.models import Sum,Count,Case,When,FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import RawSQL
from django.db.models import Q

from admssapp.updateledger import update


def updatetrans(fapploanid, loginlocationcode, loginrundate):
    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)
    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
    alatefees = loanledsumm1.get("totlatefee")


    loanleddep = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).values('locationcode','loanid').aggregate(noofentry=Coalesce(Count('loanid'),0),totdep=Coalesce(Sum('amount'),0),prindep=Coalesce(Sum('prinamt'),0),intdep=Coalesce(Sum('intamt'),0),latefee=Coalesce(Sum('latefee'),0))
    totdep = loanleddep.get("totdep")
    prindep = loanleddep.get("prindep")
    intdep = loanleddep.get("intdep")
    latefee = loanleddep.get("latefee")


    if (loanmast.apploanamt + loanmast.apploanint) < totdep:
        totdep = loanmast.apploanamt + loanmast.apploanint

    loanmast.apptotalrecamt = totdep
    loanmast.appprinrecamt =  prindep
    loanmast.appintrecamt = intdep
    loanmast.applatefeeamt = latefee
    loanmast.save()

    prevemidate = loanmast.apploandate

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
    fextradepamt = 0


    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('-date')
    if loanled:
        lastdepdate = loanled[0].date


    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

    flastdepdate = loanmast.apploandate
    for a in loanled:
        ######## Extra Intrest ########
        fdepamt = fdepamt + a.amount

        if (a.date - loanmast.apploandate).days <= loanmast.apploantenr:
            fcaldepdate = a.date
            fcaldepamt = fcaldepamt + a.amount

        elif (a.date - loanmast.apploandate).days > loanmast.apploantenr:
            fextradepamt = fextradepamt + a.amount

       
        ######## Extra Intrest ########
        
        fdelaydays = 0
        noemi = int((a.amount)/loanmast.apploanemi)
        #print(prevemidate, a.date,(a.date - prevemidate).days, emifreqdays*noemi)
        if noemi < 1:
            noemi = 1


        if (a.date - flastdepdate).days > emifreqdays*noemi:
            fdelaydays = (a.date - flastdepdate).days - emifreqdays*noemi

            #if (a.date - loanmast.apploandate).days > loanmast.apploantenr:
            #    fdelaydays = 0
            
            if fdelaydays < 0:
                fdelaydays = 0
                
            if fdelaydays > 0:
                totaldelaydays = totaldelaydays + fdelaydays
        

        a.duedate = prevemidate+timedelta(days=emifreqdays*noemi)
        a.delaydays = fdelaydays
        prevemidate = a.date
        a.save()

        flastdepdate = a.date 

  
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

    fappname = loanmast.appname
    fapploanid = loanmast.loanid
    fapploanamt = loanmast.apploanamt
    fapploanint = loanmast.apploanint
    fapploanemi = loanmast.apploanemi
             
    fapploandate = loanmast.apploandate
    fapploantenr = loanmast.apploantenr
    delta = loginrundate - loanmast.apploandate
    fapploandays = delta.days
    fappshoplocation = loanmast.appshoplocation
    fappoccupation =  loanmast.appoccupation
    fappemifreq = loanmast.appemifreq
    fapplastemidepdate = loanmast.applastemidepdate
    fapplastemidepday = ''
    if fapplastemidepdate is not None:
        fapplastemidepday = loanmast.applastemidepdate.strftime('%A')                    
    fappemiduedate = loanmast.appemiduedate
    fappoccupation = loanmast.appoccupation
    fappshopadd = loanmast.appshopadd
    fappshoplocation = loanmast.appshoplocation
    floantype =  loanmast.loantype
    fapplifeinsurdate = loanmast.applifeinsurdate
    fapplifeinsuruptodate = loanmast.applifeinsuruptodate
    fappmobileno = loanmast.appmobileno
    fcolldaychar = loanmast.colldaychar
    frpersonname = loanmast.rpersonname
    fassociatename = loanmast.associatename
    fadminpersonname = loanmast.adminpersonname
    flatefees = alatefees
    balprin = fapploanamt - prindep
                    
    ftenrexpireon = fapploandate + timedelta(days=fapploantenr)

    
    fapptotalrecamt = totdep
    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
    fapptotalbalamt = loanmast.apploanamt + loanmast.apploanint - (prindep + intdep)
   
    if fapptotalbalamt < 0:
        fapptotalbalamt = 0



    latefee = int((loanmast.apploanamt/1000) * fdelaydays)                          

    acurrdueamt = 0
    afcurrdueamt = 0
    afexcessint = 0
    fappbalamt = 0
                

    if floantype == 'INDIVIDUAL':

        if loanmast.apploandate <= datetime.strptime('2021-10-19', '%Y-%m-%d').date():
            rate = Rate.objects.get(days=360, date='2021-10-19')
            frate = rate.rate
        elif loanmast.apploandate >= datetime.strptime('2021-10-20', '%Y-%m-%d').date():
            rate = Rate.objects.get(days=334, date='2021-10-20')
            frate = rate.rate
                        
        if fapploandays > fapploantenr:
                            
            fappbalamt = loanmast.apploanamt + loanmast.apploanint - fcaldepamt
            delta = (loginrundate - fcaldepdate)
            fcaldays = int(delta.days/30) + 1
            fcaldays = fcaldays*30
                           
            nint = (fappbalamt*(frate))/100
            fint=round((nint*fcaldays)/180)

            prinbal = fapploanamt - prindep
            if prinbal < 0:
                prinbal = 0
                
            acurrdueamt = fapploanamt+fapploanint+fint
            fcurrdueamt = (fapploanamt+fapploanint+fint) - prindep - intdep
            fexcessint = fint



                             
        else:

            delta = (loginrundate - fapploandate)
            fcaldays = int(delta.days)
                           
            if loanmast.apploandate <= datetime.strptime('2021-10-19', '%Y-%m-%d').date():
                if fcaldays > 30 and fcaldays <= 60:
                    fcaldays = 60

                elif fcaldays > 60 and fcaldays <= 90:
                    fcaldays = 90

                elif fcaldays > 90 and fcaldays <= 120:
                    fcaldays = 120

                elif fcaldays > 120 and fcaldays <= 180:
                    fcaldays = 180

                elif fcaldays > 180:
                    fcaldays = 270

                                 
            elif loanmast.apploandate >= datetime.strptime('2021-10-20', '%Y-%m-%d').date():

                if fcaldays <= 90:
                    fcaldays = 90

                elif fcaldays > 90 and fcaldays <= 180:
                    fcaldays = 180

                elif fcaldays > 180 and fcaldays <= 270:
                    fcaldays = 270

                elif fcaldays > 270:
                    fcaldays = 334

                             
            nint = (fapploanamt*(frate))/100
            fint = round((nint*fcaldays)/180)
                             
            currdueamt = fapploanamt + fint
            fcurrdueamt = fapploanamt + fint - (prindep + intdep)
            fexcessint = fint - fapploanint 
                             
        totaldays = (loginrundate - loanmast.apploandate).days

        if fappemifreq == "WEEKLY":
            ftotalemidue = round(float(loanmast.apploantenr/7), 2)
            fcurremidue = round(float(totaldays/7), 2)

        elif fappemifreq == "DAILY":
            ftotalemidue = round(float(loanmast.apploantenr/1), 2)
            fcurremidue = round(float(totaldays/1), 2)

        elif  fappemifreq == "MONTHLY":
            ftotalemidue = round(float(loanmast.apploantenr/30), 2)
            fcurremidue = round(float(totaldays/30), 2)

        elif  fappemifreq == "FORTNIGHTLY":
            ftotalemidue = round(float(loanmast.apploantenr/15), 2)
            fcurremidue = round(float(totaldays/15), 2)
                        
        if fcurremidue > ftotalemidue:
            fcurremidue = ftotalemidue
            
        fcurremidone = round(float(loanmast.apptotalrecamt/loanmast.apploanemi), 2)
        fcurremibal = round(float(fcurremidue - fcurremidone), 2)
                        
        if fcurremibal < 0:
            fcurremibal = 0
        fcurroverdue =  int(fcurremibal*loanmast.apploanemi)

        if totaldays >= loanmast.apploantenr:
            tenuoverdue =  totaldays - loanmast.apploantenr
            if fappemifreq == "WEEKLY":
                ftenuoverdue = round(float(tenuoverdue/7), 2)
            elif fappemifreq == "DAILY":
                ftenuoverdue = round(float(tenuoverdue/1), 2)
            elif  fappemifreq == "MONTHLY":
                ftenuoverdue = round(float(tenuoverdue/30), 2)
            elif  fappemifreq == "FORTNIGHTLY":
                ftenuoverdue = round(float(tenuoverdue/15), 2)
        else:
            ftenuoverdue = round(float(0), 2)

        
        if (fapploanamt - prindep) > 0:

            if fcurrdueamt < (fapploanamt - prindep):
                fcurrdueamt = (fapploanamt - prindep)

        # if fcurrdueamt > fapptotalbalamt:
        #     fminamt = afcurrdueamt
        # else:
        #     fminamt = fcurrdueamt

                            

    elif floantype == 'GROUP' : 

        rate = Rate.objects.get(days=360, date='2021-10-19')
        frate = rate.rate
                        
        if fapploandays > fapploantenr:
            fappbalamt = loanmast.apploanamt + loanmast.apploanint - fcaldepamt
            delta = (loginrundate - fcaldepdate)
                             
            fcaldays = int(delta.days/30) + 1
            fcaldays = fcaldays*30

            nint = (fappbalamt*(frate))/100
            fint=round((nint*fcaldays)/360)

            acurrdueamt = fapploanamt+fapploanint+fint
            fcurrdueamt = (fapploanamt+fapploanint+fint) - prindep - intdep
            fexcessint = fint

        else:
                   

            delta = (loginrundate - fapploandate)
            fcaldays = int(delta.days/30) + 1

            if fcaldays > 9:
                fcaldays = 12
                fcaldays = fcaldays*30

            nint = (fapploanamt*(frate))/100
            fint = round((nint*fcaldays)/360)

            currdueamt = fapploanamt+fint
            fcurrdueamt = fapploanamt+fint-fapptotalrecamt

            if (fapploanamt - prindep) > 0:
                if fcurrdueamt < (fapploanamt - prindep):
                    fcurrdueamt = (fapploanamt - prindep)

            fexcessint = fint - fapploanint 

        totaldays = (loginrundate - loanmast.apploandate).days
        ftotalemidue = round(float(loanmast.apploantenr/15), 2)
      

        fcurremidue = round(float(totaldays/15), 2)

        if fcurremidue > ftotalemidue:
            fcurremidue = ftotalemidue
        fcurremidone = round(float(loanmast.apptotalrecamt/loanmast.apploanemi), 2)
        fcurremibal = round(float(fcurremidue - fcurremidone), 2)
            
        if fcurremibal < 0:
            fcurremibal = 0
        fcurroverdue =  int(fcurremibal*loanmast.apploanemi)

        ftenuoverdue = round(float(0), 2)   
        if totaldays >= loanmast.apploantenr:
            tenuoverdue =  totaldays - loanmast.apploantenr
            ftenuoverdue = round(float(tenuoverdue/15), 2)
        else:
            ftenuoverdue = round(float(0), 2)
 
    
    # if fapptotalbalamt <= 0:
    #     fcurrdueamt = 0

 

    #fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

    #print(fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue, fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin)

    return(fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue, fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin )
                            
                
