from admssapp.models import Loanmaster, Loanscheme, Personmaster
from admssapp.models import Locationlogin, Daybook, Loantrans, Rate
from datetime import datetime
from datetime import timedelta

from django.db.models import Sum,Count,Case,When,FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import RawSQL
from django.db.models import Q

from admssapp.updateledger import update


def statices(fapploanid, loginlocationcode, loginrundate):
    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)
    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

    if loanmast.appemifreq == 'DAILY':
        emifreqdays = 1
    elif loanmast.appemifreq == 'WEEKLY':
        emifreqdays = 7
    elif loanmast.appemifreq == 'FORTNIGHTLY':
        emifreqdays = 15
    elif loanmast.appemifreq == 'MONTHLY':
        emifreqdays = 30

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
    flatefees = loanledsumm1.get("totlatefee")
                    
    ftenrexpireon = fapploandate + timedelta(days=fapploantenr)

    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

    fapptotalrecamt = loanmast.apptotalrecamt
    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt

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

            acurrdueamt = fapploanamt+fapploanint+fint
            fcurrdueamt = (fapploanamt+fapploanint+fint)-fapptotalrecamt
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
                             
            currdueamt = fapploanamt+fint
            fcurrdueamt = fapploanamt+fint-fapptotalrecamt
            fexcessint = fint - fapploanint 
                             
        totaldays = (loginrundate - loanmast.apploandate).days


        ftotalemidue = round(float(loanmast.apploantenr/7), 2)
        fcurremidue = round(float(totaldays/7), 2)

        if fappemifreq == "WEEKLY":
            ftotalemidue = round(float(loanmast.apploantenr/7), 2)
            fcurremidue = round(float(totaldays/7), 2)

        elif fappemifreq == "DAILY":
            ftotalemidue = round(float(loanmast.apploantenr/1), 2)
            fcurremidue = round(float(totaldays/1), 2)

        elif fappemifreq == "FORTNIGHTLY":
            ftotalemidue = round(float(loanmast.apploantenr/1), 2)
            fcurremidue = round(float(totaldays/15), 2)

        elif  fappemifreq == "MONTHLY":
            ftotalemidue = round(float(loanmast.apploantenr/30.4), 2)
            fcurremidue = round(float(totaldays/30.4), 2)

                        
        if fcurremidue > ftotalemidue:
            fcurremidue = ftotalemidue
            
        fcurremidone = round(float(loanmast.apptotalrecamt/loanmast.apploanemi), 2)
        fcurremibal = round(float(fcurremidue - fcurremidone), 2)
                        
        if fcurremibal < 0:
            fcurremibal = 0
        fcurroverdue =  int(fcurremibal*loanmast.apploanemi)


        if totaldays >= loanmast.apploantenr:
            tenuoverdue =  totaldays - loanmast.apploantenr
            ftenuoverdue = round(float(tenuoverdue/7), 2)
            if fappemifreq == "WEEKLY":
                ftenuoverdue = round(float(tenuoverdue/7), 2)
            elif fappemifreq == "DAILY":
                ftenuoverdue = round(float(tenuoverdue/1), 2)
            elif  fappemifreq == "MONTHLY":
                ftenuoverdue = round(float(tenuoverdue/30.4), 2)
            elif  fappemifreq == "FORTNIGHTLY":
                ftenuoverdue = round(float(tenuoverdue/15), 2)

        else:
            ftenuoverdue = round(float(0), 2)

        if fcurrdueamt > fapptotalbalamt:
            fminamt = afcurrdueamt
        else:
            fminamt = fcurrdueamt
                            

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
            fcurrdueamt = (fapploanamt+fapploanint+fint)-fapptotalrecamt
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
            
        if totaldays >= loanmast.apploantenr:
            tenuoverdue =  totaldays - loanmast.apploantenr
            ftenuoverdue = round(float(tenuoverdue/15), 2)
        else:
            ftenuoverdue = round(float(0), 2)

    return(fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue)
                            
                
