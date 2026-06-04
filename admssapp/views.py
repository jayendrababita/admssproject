import csv
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models.fields import FloatField
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import never_cache

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import  get_token

from django.template import RequestContext

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages

from admssapp.utils import render_to_pdf

from django.template import loader, Context

from django.contrib import auth
from django.contrib.auth.models import User
from admssapp.models import Locationlogin
from admssapp.models import Loanmaster,Loanscheme,Personmaster
from admssapp.models import Locationlogin,Loantrans
from admssapp.models import Daybook
from admssapp.models import Transcd
from admssapp.models import Personmaster
from admssapp.models import Emicolldata
from admssapp.models import Groupemicolldata
from admssapp.models import Fundmaster,Fundmasteroth
from admssapp.models import Fundtrans
from admssapp.models import Rate
from admssapp.models import Opclcashbank
from admssapp.models import Opcltmp
from admssapp.models import Userlogged
from admssapp.models import Fundsendreceive
from admssapp.models import Authcenterexpance
from admssapp.models import Advancesmaster
from admssapp.models import Advancestrans
from admssapp.models import Generalloanmaster
from admssapp.models import Generalloantrans
from admssapp.models import Loanlead
from admssapp.models import Loanleadsumm
from admssapp.models import Emisundry

from num2words import num2words
from decimal import Decimal
from django.utils import timezone
import datetime
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
import calendar
from django.db.models import Sum,Count,Case,When,FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import RawSQL
from django.db.models import Q
from calendar import monthrange
from itertools import chain 

from django.contrib.sessions.models import Session

from admssapp.updateledger import update
from admssapp.updateemi import statices
from admssapp.updatetrans import updatetrans

from admssapp.periodicemi import updateamount


#################################
############# HOME ##############
#################################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def home(request):
                loguserid = request.session['loguserid']
                ll=Locationlogin.objects.get(user=loguserid)
        
                loginlocationcode=ll.locationcode
                loginlocationname=ll.locationname
                loginrundate=ll.rundate
                loginstatus=ll.status
                currdate = date.today()

                ip = request.session.get('ip', 0)
                x_forw = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forw:
                    ip = x_forw.split(',')[-1].strip
                else:
                    ip = request.META.get('REMOTE_ADDR')

                user = User.objects.get(id=loguserid)

                if user is not None and loginstatus in(['B','A']):


                       ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                       ftodate = ffromdate + timedelta(days=5)
          
                       nac = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year = loginrundate.year,locationcode=loginlocationcode,status="A").aggregate(total = Count("loanid"))
                       namt = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year = loginrundate.year,locationcode=loginlocationcode,status="A").aggregate(total = Sum("apploanamt"))
        
                       last_7_days = loginrundate - timedelta(days=7)
                       last_14_days = loginrundate - timedelta(days=14)
                       last_37_days = loginrundate - timedelta(days=37)

                       iracdaily = Loanmaster.objects.filter(applastemidepdate__lte=last_7_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode,status="A",appemifreq='DAILY').aggregate(total = Count("loanid"))
                       iramtdaily = Loanmaster.objects.filter(applastemidepdate__lte=last_7_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode, status="A",appemifreq='DAILY').aggregate(total=Sum("apploanemi"))


                       iracweekly = Loanmaster.objects.filter(applastemidepdate__lte=last_14_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode,status="A",appemifreq='WEEKLY').aggregate(total = Count("loanid"))
                       iramtweekly = Loanmaster.objects.filter(applastemidepdate__lte=last_14_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode, status="A",appemifreq='WEEKLY').aggregate(total=Sum("apploanemi"))


                       iracmonthly = Loanmaster.objects.filter(applastemidepdate__lte=last_37_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode,status="A",appemifreq='MONTHLY').aggregate(total = Count("loanid"))
                       iramtmonthly = Loanmaster.objects.filter(applastemidepdate__lte=last_37_days, appemiduedate__lt=last_14_days,locationcode=loginlocationcode, status="A",appemifreq='MONTHLY').aggregate(total=Sum("apploanemi"))
                    



                       emiduesumm =  Loanmaster.objects.filter(locationcode=loginlocationcode,status="A",instoverdue__gte=2).aggregate(totac=Count("loanid"), totdueamt=Sum("instoverdueamt"))


                       allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A')).order_by('colldaynum','applastemidepdate')

                       sac = Loanmaster.objects.filter(apploansettlementdate__month = loginrundate.month,apploansettlementdate__year = loginrundate.year,locationcode=loginlocationcode,status="C").aggregate(total = Count("loanid"))
                       samt = Loanmaster.objects.filter(apploansettlementdate__month = loginrundate.month,apploansettlementdate__year = loginrundate.year,locationcode=loginlocationcode,status="C").aggregate(total = Sum("apploanamt"))

                       
                       tac = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & (Q(appemiduedate__lte=ftodate) | Q(applastemidepdate__gte=ffromdate))).aggregate(total=Coalesce(Count('loanid'),0))
                       tamt = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & (Q(appemiduedate__lte=ftodate) | Q(applastemidepdate__gte=ffromdate))).aggregate(total=Coalesce(Sum('apploanamt'),0))
                       temi = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & (Q(appemiduedate__lte=ftodate) | Q(applastemidepdate__gte=ffromdate))).aggregate(
                           total=Coalesce(Sum('apploanemi'), 0))

                       eac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                       eamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))

                       fac = Loanmaster.objects.filter(applastemidepdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status='A').aggregate(total=Coalesce(Count('loanid',distinct=True),0))

                       invmis = Fundmaster.objects.filter(locationcode=loginlocationcode,inttype='MIS',mis='Y',misamount__gt=0,intduedate__lte=loginrundate,status='A').order_by('personcode')
                       
                       todayday = loginrundate.day
                       todaymonth = loginrundate.month
                       
                       birthday = Personmaster.objects.filter(locationcode=loginlocationcode,dob__day=todayday,dob__month=todaymonth) 
                       anniversary = Personmaster.objects.filter(locationcode=loginlocationcode,dom__day=todayday,dom__month=todaymonth) 
                       
                       pendingfi = Loanlead.objects.filter(locationcode=loginlocationcode,status='A')

                       
                       scrolltext = ''
                       for all in invmis:
                           scrolltext = scrolltext + "*** "+all.personname+"/"+all.relatedpersonname+"/"+str(all.misamount)+'/'+all.date.strftime('%d-%m-%Y')+'/due on '+all.intduedate.strftime('%d-%m-%Y')+" *** "

                       scrollbirthday = ''
                       for all in birthday:
                           scrollbirthday = scrollbirthday + "*** Happy Birthday Mr. "+all.personname+' '+all.dob.strftime('%d')+' '+all.dob.strftime('%B')+" *** "

                       scrollanniversary = ''
                       for all in anniversary:
                           scrollanniversary = scrollanniversary + "*** Happy Anniversary Mr. "+all.personname+' '+all.dom.strftime('%d')+' '+all.dom.strftime('%B')+" *** "

                       scrollpendingfi = ''
                       for all in pendingfi:
                           if all.fistatus1 == 'N':
                               scrollpendingfi = scrollpendingfi + "### FI-1 pending / "+all.appname+" / "+all.leadpersonname+" ### "
                           if all.fistatus2 == 'N':
                               scrollpendingfi = scrollpendingfi + "### FI-2 pending /"+all.appname+" / "+all.secondpersonname+" ### "
 

                       newac = nac.get("total")
                       newamt = namt.get("total")
   
                       settleac = sac.get("total")
                       settleamt = samt.get("total")

                       totalac = tac.get("total")
                       totalamt = tamt.get("total")
                       totalemi = temi.get("total")

                       emiac = eac.get("total")
                       emiamt = eamt.get("total")

                       fmiac = fac.get("total")



                       iregacdaily = iracdaily.get("total")
                       iregamtdaily = iramtdaily.get("total")

                       iregacweekly = iracweekly.get("total")
                       iregamtweekly = iramtweekly.get("total")

                       iregacmonthly = iracmonthly.get("total")
                       iregamtmonthly = iramtmonthly.get("total")

                       if iregacdaily is not None:
                            iregacdaily = int(iregacdaily)
                       else:
                            iregacdaily = 0 

                       if iregacweekly is not None:
                            iregacweekly = int(iregacweekly)
                       else:
                            iregacweekly = 0 

                       if iregacmonthly is not None:
                            iregacmonthly = int(iregacmonthly)
                       else:
                            iregacmonthly = 0 


                       iregac = iregacdaily + iregacweekly + iregacmonthly
 



                       deemi = emiduesumm.get("totac")


                       if totalac!=0:
                           emicoll = round(fmiac*100/totalac)
                       else:
                           emicoll= 0
                           
                       fmonth = ll.rundate.strftime("%b")
                       fyear = ll.rundate.year
                               
                       start_week = loginrundate - timedelta(loginrundate.weekday())
                       end_week = start_week + timedelta(5)

                       start_week = start_week.strftime("%d'%b%y")
                       end_week = end_week.strftime("%d'%b%y")



                       #scrolltext = 'ADMSS Micro Finance Pvt. Ltd.'

                       context={'loginlocationcode' : loginlocationcode,
                               'loginlocationname' : loginlocationname,
                               'loginrundate' : loginrundate,
                               'loginstatus' : loginstatus,
                               'currdate':currdate,
                               'ip':ip,
                               'newac' : newac,
                               'newamt' : newamt,
                               'settleac' : settleac,
                               'settleamt' : settleamt,
                               'emiac' : emiac,
                               'emiamt' : emiamt,
                               'totalac' : totalac,
                               'totalamt' : totalamt,
                               'totalemi' : totalemi,
                               'fmonth' : fmonth,
                               'fyear' : fyear,
                               'start_week' : start_week,
                               'end_week' : end_week,
                               'emicoll' : emicoll,
                               'iregac' : iregac,
                               'iregamt' : iregac,
                               'last_14_days' : last_14_days,
                               'deemi':deemi,
                               'scrolltext': scrolltext,
                               'scrollbirthday':scrollbirthday,
                               'scrollanniversary':scrollanniversary,
                               'scrollpendingfi':scrollpendingfi,
                                }

                

                       template = loader.get_template('admssapp/home.html')

                       return HttpResponse(template.render(context, request))
  

                elif user is not None and loginstatus in(['H']):

                        return redirect('admssadminhome/')
    
                elif user is not None and loginstatus in(['C']):

                        return redirect('admsscollhome/')

                elif user is not None and loginstatus in(['I']):

                        return redirect('admssinsurancehome/')                        
                else:
                        return render(request, 'admssapp/login.html', context)




########################
######## LOGIN #########
########################
@csrf_exempt
@never_cache
def login(request):
        if request.method == "POST":
             request.session.flush()

             user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
             if user is not None and request.POST.get('password') == 'newpassword':

                 return render(request, 'admssapp/resetpassword.html')

             if user is None:
                 success=True
                 message="Invalid Credentials..."
                 context={
                   'success':success,
                   'message':message,
                         }
                 return render(request, 'admssapp/login.html', context)
             else:

                loguser = User.objects.get(username=request.POST.get('username'))
                loguserid = loguser.id
                logusername = loguser.username
                logname = loguser.last_name


                try:
                    ll=Locationlogin.objects.get(user_id=loguserid)
             
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    loginstatus=ll.status
                    currdate = date.today()
                
                    request.session['loguserid'] = loguserid
                
                    #### IP ####

                    ip = request.session.get('ip', 0)
                    x_forw = request.META.get('HTTP_X_FORWARDED_FOR')

                    if x_forw:
                        ip = x_forw.split(',')[-1].strip()
                    else:
                        ip = request.META.get('REMOTE_ADDR')


      
                    context={'loginlocationcode':loginlocationcode,
                         'loginlocationname':loginlocationname,
                         'loginrundate':loginrundate,
                         'loguserid':loguserid,
                         'loginstatus':loginstatus,
                         'currdate':currdate,
                         }
      

                    if user is not None and loginstatus in(['B','A']):
                  
                        Locationlogin.objects.filter(user=loguser).update(lastlogin=datetime.now(),ip=ip) 
                        lu = Userlogged(locationcode=loginlocationcode,locationname=loginlocationname,rundate=loginrundate,logindatetime=datetime.now(),user=loguser,username=logusername,ip=ip)
                        lu.save()
                        auth.login(request, user)

                        #return render(request, 'admssapp/home.html', context)
                        return redirect('home')
              
                    elif user is not None and loginstatus in(['H']):
                        Locationlogin.objects.filter(user=loguser).update(lastlogin=datetime.now(),ip=ip) 
                        lu = Userlogged(locationcode=loginlocationcode,locationname=loginlocationname,rundate=loginrundate,logindatetime=datetime.now(),user=loguser,username=logusername,ip=ip)
                        lu.save()
                        auth.login(request, user)

                        #return render(request, 'admssadmin/home.html', context)
                        return redirect('admssadminhome/')
   
    
                    elif user is not None and loginstatus in(['C']):
                        Locationlogin.objects.filter(user=loguser).update(lastlogin=datetime.now(),ip=ip) 
                        lu = Userlogged(locationcode=loginlocationcode,locationname=loginlocationname,rundate=loginrundate,logindatetime=datetime.now(),user=loguser,username=logusername,ip=ip)
                        lu.save()
                        auth.login(request, user)

                        #return render(request, 'admsscoll/admsscollhome.html',context)
                        return redirect('admsscollhome/')

                    elif user is not None and loginstatus in(['I']):
                        Locationlogin.objects.filter(user=loguser).update(lastlogin=datetime.now(),ip=ip) 
                        lu = Userlogged(locationcode=loginlocationcode,locationname=loginlocationname,rundate=loginrundate,logindatetime=datetime.now(),user=loguser,username=logusername,ip=ip)
                        lu.save()
                        auth.login(request, user)

                        #return render(request, 'admsscoll/admsscollhome.html',context)
                        return redirect('admssinsurancehome/')




                    else:
                        success=True
                        message="Invalid Credentials..."
                        context={
                         'success':success,
                         'message':message,
                             }

                        return render(request, 'admssapp/login.html', context)
    
                except Locationlogin.DoesNotExist:
                    success=True
                    message="Invalid Credentials..."
                    context={
                      'success':success,
                      'message':message,
                         }

                    return render(request, 'admssapp/login.html', context)

        else:
            return render(request, 'admssapp/login.html')


##############################
######## RESET LOGIN #########
##############################
@csrf_exempt
@never_cache
def resetlogin(request):
        if request.method == "POST":
             request.session.flush()

             fusername = request.POST.get('username')
             fpassword = request.POST.get('password')
             fconfirmpassword = request.POST.get('repassword')

             user = User.objects.get(username=fusername)
            
             if user.username is not None and fpassword==fconfirmpassword:

                 user.password = fpassword
                 user.set_password(fpassword)
                 user.save()

                 success=True
                 message="Password Change Successfully..."
                 context={
                   'success':success,
                   'message':message,
                         }
              
                 return render(request, 'admssapp/login.html', context)
             else:
                 return render(request, 'admssapp/login.html')
        else:
            return render(request, 'admssapp/login.html')



###################
#### NEW LOAN  ####
###################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def newloan(request):
        

        loguserid = request.session['loguserid']
        ll=Locationlogin.objects.get(user=loguserid)
            
        loginlocationcode=ll.locationcode
        loginlocationname=ll.locationname
        loginrundate=ll.rundate
        loginstatus=ll.status
        currdate = date.today()

        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
        else:

                rundatevalue = loginrundate.strftime("%Y-%m-%d") 

                allloansch = Loanscheme.objects.filter(loanamt__gt=0).distinct('loanamt').order_by('loanamt')
                alldays = Loanscheme.objects.filter(loandays__lte=365).distinct('loandays').order_by('loandays')
                allfreq = Loanscheme.objects.filter().distinct('emifreq').order_by('emifreq')     
            
                allcoll = Personmaster.objects.filter(locationcode=loginlocationcode,persontype='COLL').distinct().order_by('personname')
                allasso = Personmaster.objects.filter(locationcode=loginlocationcode, persontype__in=['COLL','DASS']).distinct().order_by('personname')
                alladmin = Personmaster.objects.filter(locationcode=loginlocationcode, admin='Y').distinct().order_by('personname')
                allgroup = Loanmaster.objects.filter(locationcode=loginlocationcode,groupleader='Y').distinct().order_by('groupid')
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y').order_by('bankac')
                allloanmast = Loanmaster.objects.filter(locationcode=loginlocationcode).order_by('appname','-apploandate')
               

                context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'allloanmast':allloanmast,
                                }



                if request.method == "POST":
                    floantype = request.POST.get('loantype')
                    foldloanid = request.POST.get('oldloanid')
            
                    
                    if floantype == 'New Borrower':
                        context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'rundatevalue':rundatevalue,
                        'allloansch': allloansch,
                        'alldays': alldays,
                        'allfreq': allfreq,
                        'allcoll': allcoll,
                        'allasso': allasso,
                        'allgroup': allgroup,
                        'allbank': allbank,
                        'alladmin': alladmin,
                        'allloanmast': allloanmast,
                        }
                        return render(request, 'admssapp/newloanentryNB.html', context)    

                    else:
                        
                        oldid = Loanmaster.objects.get(loanid=foldloanid)
                        fappname=oldid.appname
                        fapptitle=oldid.apptitle
                        fappmaritalstatus=oldid.appmaritalstatus
                        fappgender = oldid.appgender
                        fappdob = oldid.appdob.strftime("%Y-%m-%d")

                        fcoappname=oldid.coappname
                        fcoapprelation=oldid.coapprelation

                        fcoappdob = oldid.coappdob
                        if oldid.coappdob is not None:
                            fcoappdob = oldid.coappdob.strftime("%Y-%m-%d")
                        else:
                            fcoappdob = "2008-08-31"   

                        fcoappmobileno=oldid.coappmobileno
                        fcoappadharno = ''
                        fcoappgender = oldid.coappgender
                        fcoappadharno = oldid.coappadharno
                        fcoapppanno = ''

                        fappfathername=oldid.appfathername
                        fappadharno=oldid.appadharno
                        fapppanno=oldid.apppanno
                        fappmobileno=oldid.appmobileno
                        fappnoofdependent=oldid.appnoofdependent
                        fapppresentadd=oldid.apppresentadd
                        fapppresentaddlandmark=oldid.apppresentaddlandmark
                        fapppresentaddcity=oldid.apppresentaddcity
                        fapppresentaddpin=oldid.apppresentaddpin
                        fapppermanentadd=oldid.apppermanentadd
                        fapppermanentaddcity=oldid.apppermanentaddcity
                        fapppermanentaddpin=oldid.apppermanentaddpin
                        fguarname=oldid.guarname
                        fguarfathername=oldid.guarfathername

                        if oldid.guardob is not None:
                            fguardob = oldid.guardob.strftime("%Y-%m-%d")
                        else:
                            fguardob = "2002-08-31"  

                        fguargender=oldid.guargender
                        fguaradharno=oldid.guaradharno
                        fguarpanno=oldid.guarpanno
                        fguarrelation=oldid.guarrelation
                        fguarpresentadd=oldid.guarpresentadd
                        fguarpresentaddcity=oldid.guarpresentaddcity
                        fguarpresentaddpin=oldid.guarpresentaddpin
                        fguarmobileno=oldid.guarmobileno
                        fappoccupation=oldid.appoccupation
                        fappshopdetail=oldid.appshopdetail
                        fappshopadd=oldid.appshopadd
                        fappshoplocation=oldid.appshoplocation
                        fappdailysale=oldid.appdailysale
                        fappdailyincome=oldid.appdailyincome
                        fapploanpurpose=oldid.apploanpurpose
                        fguaroccupation=oldid.guaroccupation
                        fguaroccupationadd=oldid.guaroccupationadd
                        fappchq=oldid.appchq
                        if fappchq == '' or fappchq == None:
                            fappchq = 'No'

                        fappchqno1=oldid.appchqno1
                        fappchqno2=oldid.appchqno2
                        fappbankac=oldid.appbankac
                        fappbankname=oldid.appbankname
                        fappbankifsc=oldid.appbankifsc
                        fappbankbranch=oldid.appbankbranch
                        fappnameasbank = oldid.appnameasbank
                        frpersoncode = oldid.rpersoncode
                        frpersonname = oldid.rpersonname
                        fadminpersonname = oldid.adminpersonname
                        fadminpersoncode = oldid.adminpersoncode
                        fadminpersonname = oldid.adminpersonname
                        fappchq = oldid.appchq
                        
                        if oldid.appchqno1 is not None:
                            pass
                        else:
                            fappchqno1 = ' '

                        if oldid.appchqno2 is not None:
                            pass
                        else:
                            fappchqno2 = ' '

                     
                        context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'rundatevalue':rundatevalue,
                            'allloansch': allloansch,
                            'alldays': alldays,
                            'allfreq': allfreq,
                            'allcoll': allcoll,
                            'alladmin':alladmin,
                            'allasso': allasso,
                            'allgroup': allgroup,
                            'allbank': allbank,
                            'allloanmast': allloanmast,
                            'fapptitle':fapptitle,
                            'fappmaritalstatus':fappmaritalstatus,
                            'fappname':fappname,
                            'fappgender':fappgender,
                            'fappdob':fappdob,
                            'fcoappname':fcoappname,
                            'fcoapprelation':fcoapprelation,
                            'fcoappmobileno':fcoappmobileno,
                            'fcoappdob':fcoappdob,
                            'fcoappgender':fcoappgender,
                            'fcoappadharno':fcoappadharno,
                            'fcoapppanno':fcoapppanno,
                            'fappfathername':fappfathername,
                            'fappadharno':fappadharno,
                            'fapppanno':fapppanno,
                            'fappmobileno':fappmobileno,
                            'fappnoofdependent':fappnoofdependent,
                            'fapppresentadd':fapppresentadd,
                            'fapppresentaddlandmark':fapppresentaddlandmark,
                            'fapppresentaddcity':fapppresentaddcity,
                            'fapppresentaddpin':fapppresentaddpin,
                            'fapppermanentadd':fapppermanentadd,
                            'fapppermanentaddcity':fapppermanentaddcity,
                            'fapppermanentaddpin':fapppermanentaddpin,
                            'fguarname':fguarname,
                            'fguarfathername':fguarfathername,
                            'fguardob':fguardob,
                            'fguargender':fguargender,
                            'fguaradharno':fguaradharno,
                            'fguarpanno':fguarpanno,
                            'fguarrelation':fguarrelation,
                            'fguarpresentadd':fguarpresentadd,
                            'fguarpresentaddcity':fguarpresentaddcity,
                            'fguarpresentaddpin':fguarpresentaddpin,
                            'fguarmobileno':fguarmobileno,
                            'fappoccupation':fappoccupation,
                            'fappshopdetail':fappshopdetail,
                            'fappshopadd':fappshopadd,
                            'fappshoplocation':fappshoplocation,
                            'fappdailysale':fappdailysale,
                            'fappdailyincome':fappdailyincome,
                            'fapploanpurpose':fapploanpurpose,
                            'fguaroccupation':fguaroccupation,
                            'fguaroccupationadd':fguaroccupationadd,
                            'fappchq':fappchq,
                            'fappchqno1':fappchqno1,
                            'fappchqno2':fappchqno2,
                            'fappbankac':fappbankac,
                            'fappbankname':fappbankname,
                            'fappbankifsc':fappbankifsc,
                            'fappbankbranch':fappbankbranch,
                            'fappnameasbank':fappnameasbank,
                            'frpersoncode':frpersoncode,
                            'frpersonname':frpersonname,
                            'fadminpersoncode':fadminpersoncode,
                            'fadminpersonname':fadminpersonname,
                            'fappchq': fappchq,
                                }

                        return render(request, 'admssapp/newloanentryEB.html', context)    
                else:
                    return render(request, 'admssapp/newloan.html', context)
            
 

##########################
#### NEW LOAN COMMIT  ####
##########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def addnewloan(request):
     
       loguserid = request.session['loguserid']
       ll=Locationlogin.objects.get(user=loguserid)
        
       loginlocationcode=ll.locationcode
       loginlocationname=ll.locationname
       loginrundate=ll.rundate
       loginstatus=ll.status
       currdate = date.today()

       user = User.objects.get(id=loguserid)
       if user is not None and loginstatus not in(['B','A']):
            return HttpResponseRedirect('/login')
       else:
   
            context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                 }

            
            if request.method == "POST":
                    flocationcode = loginlocationcode
                    fapptitle = request.POST.get('apptitle')
                    fappname = request.POST.get('appname').upper()
                    fappgender = request.POST.get('appgender')
                    fappdob = request.POST.get('appdob')
                    fappadharno=request.POST.get('appadharno')          
                    fapppanno=request.POST.get('apppanno').upper()
                    fcoappname=request.POST.get('coappname').upper()  
                    fcoapprelation=request.POST.get('coapprelation')
                    fcoappdob=request.POST.get('coappdob')  
                    fcoappgender = request.POST.get('coappgender')
                    fcoappadharno = request.POST.get('coappadharno')
                    fcoapppanno = request.POST.get('coapppanno')
                    fcoappmobileno = request.POST.get('coappmobileno')
                    fappfathername=request.POST.get('appfathername').upper()
                    fappmobileno=request.POST.get('appmobileno')
                    fapppresentadd=request.POST.get('apppresentadd').upper()
                    fapppresentaddlandmark=request.POST.get('apppresentaddlandmark').upper()
                    fapppresentaddcity=request.POST.get('apppresentaddcity').upper()
                    fapppresentaddpin=request.POST.get('apppresentaddpin')
                    fapppermanentadd=request.POST.get('apppermanentadd')
                    fapppermanentaddcity=request.POST.get('apppermanentaddcity')
                    fapppermanentaddpin=request.POST.get('apppermanentaddpin')
                    fappmaritalstatus = request.POST.get('appmaritalstatus')
                    fguarname=request.POST.get('guarname').upper()
                    fguargender=request.POST.get('guargender')
                    fguardob=request.POST.get('guardob')
                    fguarfathername=request.POST.get('guarfathername').upper()
                    fguaradharno=request.POST.get('guaradharno')  
                    fguarpanno=request.POST.get('guarpanno').upper()
                    fguarrelation=request.POST.get('guarrelation')
                    fguarpresentadd=request.POST.get('guarpresentadd').upper()
                    fguarpresentaddcity=request.POST.get('guarpresentaddcity').upper()
                    fguarpresentaddpin=request.POST.get('guarpresentaddpin')
                    fguarmobileno=request.POST.get('guarmobileno')
                    fguaroccupation=request.POST.get('guaroccupation')
                    fguaroccupationadd=request.POST.get('guaroccupationadd').upper()
                    fappoccupation=request.POST.get('appoccupation')
                    fappshopadd = request.POST.get('appshopadd').upper()
                    fappshoplocation = request.POST.get('appshoplocation').upper()
                    fappshopdetail=request.POST.get('appshopdetail').upper()

                    fapploanpurpose=request.POST.get('apploanpurpose')
                    fapploanamt=request.POST.get('apploanamt')
                    fappemifreq=request.POST.get('appemifreq').strip()
                    fapploantenr=request.POST.get('apploantenr')
                    fappbankac = request.POST.get('appbankac')
                    fappbankname = request.POST.get('appbankname')
                    fappbankifsc = request.POST.get('appbankifsc')
                    fappbankbranch = request.POST.get('appbankbranch')
                    fappnameasbank = request.POST.get('appnameasbank')

                    fappchq=request.POST.get('appchq')
                    fappchqno1=request.POST.get('appchqno1')
                    fappchqno2=request.POST.get('appchqno2')

                    fpersoncode=request.POST.get('rpersoncode')
                    fassociate=request.POST.get('associate')
                    fadmin=request.POST.get('admin')
                   
                    fapploantype=request.POST.get('apploantype').upper()
                    fappgroupleadername=request.POST.get('appgroupleadername')
                    fbankac=request.POST.get('bankac')
                    fdisbmode=request.POST.get('disbmode').upper()
                    
                    fbankchq=request.POST.get('bankchq')
                    if fbankchq:
                        fbankchq=request.POST.get('bankchq').upper()

                    fsameadd = request.POST.get('permsame')
                    fformno = request.POST.get('formno')
                    fpassbookno =  request.POST.get('passbook')
                    fapplifeinsur="N"
                    fstatus = 'A'
                    fgroupleadger=""
                    procfeereceipt = "N"

                    if fappchq == "No":
                        fappchqno = " "

                    if fsameadd=="on":
                        fapppermanentadd=fapppresentadd
                        fapppermanentaddcity=fapppresentaddcity
                        fapppermanentaddpin=fapppresentaddpin
                
                    amount = int(fapploanamt)
                    ndays = int(fapploantenr)

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

                    # daycoll = (total/ndays)
                    # weekcoll = ((total*7)/ndays)
                    # fortnightcoll = ((total*15)/ndays)
                    # monthcoll = round((daycoll*30)/ndays)

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

                        fappemiduedate = (fappemiduedate.strftime("%Y"))+(fappemiduedate.strftime("%m"))+(loginrundate.strftime("%d"))
                        fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')


                            
                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mloannum = alllocmast.loannum + 1
                    mtransidnum = alllocmast.transidnum + 1

                    coll = Personmaster.objects.get(personcode=fpersoncode, locationcode=loginlocationcode)
                    fpersonname = coll.personname
                    fpersoncode = coll.personcode
                   
                    fassociatename = ''
                    fassociatecode = ''
                    fassoexp = 'N'
                    fassoexpamt = 0
                    fassoexpstatus = ''
                    if fassociate:
                        asso = Personmaster.objects.get(personcode=fassociate,locationcode=loginlocationcode)
                        fassociatename = asso.personname
                        fassociatecode = asso.personcode
                        fassoexp = 'Y'
                        if loginstatus =='B':
                            fassoexpamt = int(fapploanamt)*.01
                        elif loginstatus =='A':
                            fassoexpamt = int(fapploanamt)*.005

                        fassoexpstatus = 'N'
                        

                    fadminpersonname = ''
                    fadminpersoncode = ''
                    admin = Personmaster.objects.get(personcode=fadmin,admin='Y')
                    fadminpersonname = admin.personname
                    fadminpersoncode = admin.personcode

                    fapploandate=loginrundate


                                
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")


                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                    if fdisbmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        if int(fapploanamt) > allbank.clbank:
                            fclfund= allbank.clbank
                            context = {'fapploanamt':fapploanamt,
                                        'fclfund':fclfund, }
                            return render(request, 'admssapp/newloanfund.html', context) 

                    if fdisbmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        if int(fapploanamt) > allcash[0].clcash:
                            fclfund= allcash[0].clcash
                            context = {'fapploanamt':fapploanamt,
                                        'fclfund':fclfund, }
                            return render(request, 'admssapp/newloanfund.html') 

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
        
                    if fapploantype=="INDIVIDUAL":
                        fidprefix="I"
                        mgroupid=0
                        fgroupleaderloanid = ""
                        fgroupleadername = ""
                        fgroupleader=""
                        fgroupid=""
                
                    if fapploantype=="GROUP":
                        fidprefix="G"
                        mgroupid=0
                        groupemicoll = 'N'

                        if fappgroupleadername=="NEW GROUP":
                            alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                            mgroupid=alllocmast.loangroupid + 1
                            alllocmast.loangroupid = alllocmast.loangroupid+1
                            fgroupid = loginlocationcode+str(mgroupid).zfill(4)
                            alllocmast.save()
                                
                            
                    floanid = fidprefix+loginlocationcode+str(mgroupid).zfill(4)+str(mloannum).zfill(4)


                    if fapploantype=="GROUP" and fappgroupleadername=="NEW GROUP":
                        fgroupleaderloanid = floanid
                        fgroupleadername = fappname
                        fgroupleader="Y"
                        fgroupid = loginlocationcode+str(mgroupid).zfill(4)
                    

                    if fapploantype=="GROUP" and fappgroupleadername!="NEW GROUP":
                        lm = Loanmaster.objects.get(locationcode=loginlocationcode, groupleader='Y', groupid = fappgroupleadername)
                        
                        fgroupleadername = lm.groupleadername
                        fgroupleaderloanid = lm.groupleaderloanid
                        fgroupid = lm.groupid
                        fgroupleader=""
                        mgroupid = fgroupid[4:8]

                    alllocmast.loannum = alllocmast.loannum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    floanid = fidprefix+loginlocationcode+str(mgroupid).zfill(4)+str(mloannum).zfill(4)
                    fcolldaychar = fappemiduedate.strftime('%A')
                    fcolldaynum =  fappemiduedate.strftime('%w')

                    lm = Loanmaster(locationcode = loginlocationcode,
                                locationname = loginlocationname,
                                loanid = floanid,
                                transid = ftransid,
                                apptitle = fapptitle,
                                appname = fappname,
                                appgender = fappgender,
                                appdob = fappdob,
                                appadharno = fappadharno,          
                                apppanno = fapppanno,
                                coappname = fcoappname,  
                                coapprelation = fcoapprelation,
                                coappdob = fcoappdob,
                                appfathername = fappfathername,
                                appmaritalstatus = fappmaritalstatus,
                                appmobileno = fappmobileno,
                                coappmobileno = fcoappmobileno,
                                coappgender = fcoappgender,
                                coappadharno = fcoappadharno,
                                coapppanno = fcoapppanno,
                                apppresentadd = fapppresentadd,
                                apppresentaddlandmark = fapppresentaddlandmark,
                                apppresentaddcity = fapppresentaddcity,
                                apppresentaddpin = fapppresentaddpin,
                                apppermanentadd = fapppermanentadd,
                                apppermanentaddcity = fapppermanentaddcity,
                                apppermanentaddpin = fapppermanentaddpin,
                                guarname = fguarname,
                                guargender = fguargender,
                                guardob = fguardob,
                                guarfathername = fguarfathername,
                                guaradharno = fguaradharno,
                                guarpanno = fguarpanno,
                                guarrelation = fguarrelation,
                                guarpresentadd = fguarpresentadd,
                                guarpresentaddcity = fguarpresentaddcity,
                                guarpresentaddpin = fguarpresentaddpin,
                                guarmobileno = fguarmobileno,
                                guaroccupation = fguaroccupation,
                                guaroccupationadd = fguaroccupationadd,
                                appoccupation = fappoccupation,
                                appshopadd = fappshopadd,
                                appshopdetail = fappshopdetail,
                                appshoplocation=fappshoplocation,
                                apploanpurpose = fapploanpurpose,
                                apploanamt = fapploanamt,
                                appemifreq = fappemifreq,
                                apploandate = fapploandate, 
                                apploantenr = fapploantenr,
                                appbankac = fappbankac,
                                appbankname = fappbankname,
                                appbankifsc = fappbankifsc,
                                appbankbranch = fappbankbranch,
                                appnameasbank = fappnameasbank,
                                appchq = fappchq,
                                appchqno1 = fappchqno1,
                                appchqno2 = fappchqno2,
                                apploanint = fapploanint,
                                apploanemi = fapploanemi,
                                apploanemiprin = fapploanemiprin,
                                apploanemiint = fapploanemiint,
                                rpersoncode = fpersoncode,
                                rpersonname = fpersonname,
                                associatecode = fassociatecode,
                                associatename = fassociatename,
                                assoexp = fassoexp,
                                assoexpamt = fassoexpamt,
                                assoexpstatus = fassoexpstatus,
                                adminpersoncode = fadminpersoncode,
                                adminpersonname = fadminpersonname,
                                loantype = fapploantype,
                                groupleaderloanid = fgroupleaderloanid,
                                groupleadername = fgroupleadername,
                                groupid = fgroupid,
                                groupleader = fgroupleader,
                                mode = fdisbmode,
                                disbchq = fbankchq,
                                appemiduedate = fappemiduedate,
                                colldaychar = fcolldaychar,
                                colldaynum =  fcolldaynum,
                                applifeinsur = fapplifeinsur,
                                passbookno = fpassbookno,
                                formno = fformno,
                                status = fstatus,
                                procfeereceipt = 'N',
                                instdue = 0.0,
                                instdone = 0.0,
                                instoverdue = 0.0,
                                instoverdueamt = 0
                                )
                    
                    lm.save()

                    ftranscd = '3010'
                    ftransnm = 'LOAN DISBURSEMENT'
                    fnarr = ftransnm.strip()+"/"+fappname
            
                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftrans = trans.id



                    if fdisbmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        opclid = allbank.id
                    
                        db = Daybook(locationcode = loginlocationcode,
                                locationname = loginlocationname,
                                loanid = floanid,
                                transid = ftransid,
                                appname = fappname,
                                amount = fapploanamt,
                                date = fapploandate,
                                transcd = ftranscd,
                                transnm = ftransnm, 
                                personcode = fpersoncode,
                                personname = fpersonname,
                                narration = fnarr,
                                bankac = fbankac,
                                mode = fdisbmode,
                                chequeno = fbankchq,
                                drcr = 'D',
                                trans_id = ftrans,
                                clcashbank_id = opclid
                                )

                        db.save()       
                    
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        fbankcd = allbank.bankcode
                        fbankname = allbank.bankname
                        opclid = allbank.id
            
                        trans = Transcd.objects.get(transcd=fbankcd)
                        ftrans = trans.id

                        db = Daybook(locationcode = loginlocationcode,
                                locationname = loginlocationname,
                                loanid = floanid,
                                transid = ftransid,
                                appname = fappname,
                                amount = fapploanamt,
                                date = fapploandate,
                                transcd = fbankcd,
                                transnm = fbankname, 
                                narration = fnarr,
                                bankac = fbankac,
                                mode = fdisbmode,
                                chequeno = fbankchq,
                                drcr = 'C',
                                trans_id = ftrans,
                                clcashbank_id = opclid)

                        db.save()
        
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        allbank.clbank=allbank.clbank-int(fapploanamt)
                        allbank.save()


                    # CASH #
                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id
                    
                    if fdisbmode == "CASH":
                        db = Daybook(locationcode = loginlocationcode,
                                locationname = loginlocationname,
                                loanid = floanid,
                                transid = ftransid,
                                appname = fappname,
                                amount = fapploanamt,
                                date = fapploandate,
                                transcd = ftranscd,
                                transnm = ftransnm, 
                                personcode = fpersoncode,
                                personname = fpersonname,
                                narration = fnarr,
                                bankac = '',
                                mode = fdisbmode,
                                chequeno = '',
                                drcr = 'D',
                                trans_id = ftrans,
                                clcashbank_id = opclid )
                        db.save()   
                        
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)    

                        for all in allcash:
                            all.clcash = all.clcash - int(fapploanamt)
                            all.save()
        
                    ftranscd = '3014'
                    ftransnm = 'PROC.FEE.'
                    fnarr = ftransnm.strip()+"/"+fappname
                    fprocfee = int(fapploanamt)*.03

                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftrans = trans.id
                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id
                    
                    db = Daybook(locationcode = loginlocationcode,
                                locationname = loginlocationname,
                                loanid = floanid,
                                transid = ftransid,
                                appname = fappname,
                                amount = fprocfee,
                                date = fapploandate,
                                transcd = ftranscd,
                                transnm = ftransnm, 
                                personcode = '',
                                personname = '',
                                narration = fnarr,
                                bankac = '',
                                mode = 'CASH',
                                chequeno = '',
                                drcr = 'C',
                                trans_id = ftrans,
                                clcashbank_id = opclid
                                )
                    db.save()  
                         
                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    for all in allcash:
                        all.clcash = all.clcash + int(fprocfee)
                        all.save()

                    rundatevalue = loginrundate.strftime("%Y-%m-%d") 

                    allloan = Loanscheme.objects.values('loanamt').distinct().order_by('loanamt')
                    alldays = Loanscheme.objects.values('loandays').distinct().order_by('loandays')
                    allfreq = Loanscheme.objects.values('emifreq').distinct().order_by('emifreq')
            
                    allcoll = Personmaster.objects.filter(locationcode=loginlocationcode,persontype='C').distinct().order_by('personname')
                    allgroup = Loanmaster.objects.filter(locationcode=loginlocationcode,groupleader='Y').distinct().order_by('groupid','apploandate')
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
        
                    allloanmast = Loanmaster.objects.filter(locationcode=loginlocationcode).order_by('appname','apploandate')
                
        
                    success = True 

                    message = "New Loan ID "+floanid+" / "+fappname+" / Generated Successfully."
                    messages.success(request, message)
                    return HttpResponseRedirect('/newloan/')
            else:
                    return render(request, 'admssapp/home.html' , context)


###########################
#### LOAN SETTLE FINAL ####
###########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loansettlement(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
            
                if request.method == "POST":

                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y').order_by('bankac')

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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    floantype =  loanmast.loantype
                    flatefees = loanmast.applatefeeamt
                    fprinbal =  loanmast.apploanamt - loanmast.appprinrecamt
                    if fprinbal <= 0 :
                        fprinbal = 0



                    fdepamt = 0
                    fcaldepamt = 0
                    fcaldepdate = 0
                    fappbalamt = 0
                    datechk="Y"
                    
                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue,  fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin= updatetrans(fapploanid, loginlocationcode, loginrundate)

                    ftotaldueamt = fapptotalbalamt



                    if ftotaldueamt <= fcurrdueamt:
                        currdueamt = fcurrdueamt
                        totaldueamt = ftotaldueamt


                        ftotaldueamt = currdueamt
                        fcurrdueamt = totaldueamt


                 

           


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapptotalbalamt':fapptotalbalamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fexcessint':fexcessint,
                            'fint':fint,
                            'fappbalamt':fappbalamt,
                            'fcurrdueamt':fcurrdueamt,
                            'ftotaldueamt':ftotaldueamt,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'allbank': allbank,
                            'fprinbal':fprinbal
                            
                        }

                    return render(request, 'admssapp/loansettlementshow.html' , context)
            
                else:
                    return render(request, 'admssapp/loansettlement.html' , context)

 


################################
#### LOAN SETTLEMENT COMMIT ####
################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loansettlementcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec =  request.POST.get('cashrec')
                    fmode = request.POST.get('emimode')
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')

                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))


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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    floantype =  loanmast.loantype
                    flatefees = loanmast.applatefeeamt
                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname
                    fmasterid = loanmast.id

                    fprinbal =  loanmast.apploanamt - loanmast.appprinrecamt

                    if fprinbal <= 0 :
                        fprinbal = 0



                    fdepamt = 0
                    fcaldepamt = 0
                    fcaldepdate = 0
                    fappbalamt = 0
                    datechk="Y"
                    
                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue,  fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin= updatetrans(fapploanid, loginlocationcode, loginrundate)

                    ftotaldueamt = fapptotalbalamt


                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'


                    fbalintamt = fint - loanmast.appintrecamt
                    fbalprinamt = loanmast.apploanamt-loanmast.appprinrecamt 


                    if fint < loanmast.apploanint:
                        fbalintamt = fint - loanmast.appintrecamt
                        loanmast.apploanint = fbalintamt 


                    if fbalprinamt <= 0:
                        fbalprinamt = 0

                    if fbalintamt <= 0:
                        fbalintamt = 0

                    flatefee = int(fcashrec) - (fbalprinamt) - (fbalintamt)



                    if flatefee <= 0:
                        flatefee = 0

                    
                    famount = int(fcashrec) - int(flatefee)


                    if famount > fbalprinamt:
                        fprinamt = fbalprinamt
                        fintamt = famount - fprinamt

                    elif famount <= fbalprinamt:
                        fprinamt = famount
                        fintamt = 0



                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 

                    ####  TRANSNUM  ####

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                    fcashrecemi = int(fcashrec) - int(flatefee)

                    remquo = divmod(fcashrecemi,fapploanemi)
                    multi = remquo[0]
                    remain = remquo[1]

                    #finstno = loanmast.instno + multi
                    #loanmast.instno = loanmast.instno + multi
                    loanmast.applastemidepdate = loginrundate


                    trans = Transcd.objects.get(transcd=femiprintranscd)
                    ftrans = trans.id

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id
                    
                    if fprinamt > 0:    
                        db1 = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=femiprintranscd,transnm=femiprintransnm,
                            mode=fmode,personcode=fpersoncode,personname=fpersonname,
                            loanid=fapploanid ,appname=fappname,
                            bankac=fappbankac,
                            narration=fnarr1,amount=fprinamt,drcr="C",
                            trans_id = ftrans,
                            clcashbank_id = opclid
                            )
            
                        db1.save()


                    trans = Transcd.objects.get(transcd=femiinttranscd)
                    ftrans = trans.id


                    if fintamt > 0: 
                                db2 = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,
                                        transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                        mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                        loanid=fapploanid ,appname=fappname,
                                        bankac=fappbankac,
                                        narration=fnarr2,amount=fintamt,drcr="C",
                                        trans_id = ftrans,
                                        clcashbank_id = opclid
                                        )

                                db2.save()      


                    trans = Transcd.objects.get(transcd=flatefeetranscd)
                    ftrans = trans.id


                    if flatefee > 0:
                                db3 = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,
                                    transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    loanid=fapploanid ,appname=fappname,
                                    bankac=fappbankac,
                                    narration=fnarr3,amount=flatefee,drcr="C",
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )

                                db3.save()
                    

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    if fintamt > 0:
                        fhqamt=fintamt*(mperc/100)
                        facamt=fintamt-fhqamt
                        for all in allcash:

                                all.hqamt = all.hqamt + fhqamt
                                all.acamt = all.acamt + facamt 

                                all.save()
            
            
                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        for all in allcash:
                            all.clcash = all.clcash + int(fcashrec) 
                            all.save()

                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            trans = Transcd.objects.get(transcd=allbank.bankcode)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            opclid = allbank.id
                        

                            fnarr="EMI DEPOSIT/"+fappname.strip()+"/"+fapploanid
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname = loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )
                            db.save()             

                    
                    if int(fcashrec) > 0:

                        lt = Loantrans(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        loanid=fapploanid,
                                        transid=ftransid,duedate=fappemiduedate,
                                        date=loginrundate,delaydays=(delta.days),
                                        amount=famount,prinamt=fprinamt,
                                        intamt=fintamt,latefee=flatefee,mode=fmode,
                                        drcr="C",master_id=fmasterid)
                                    
                        lt.save()


                    loanmast.apptotalrecamt = loanmast.apptotalrecamt + int(fcashrec)-int(flatefee)
                    loanmast.appprinrecamt = loanmast.appprinrecamt + fprinamt
                    loanmast.appintrecamt = loanmast.appintrecamt + fintamt
                    loanmast.applatefeeamt = loanmast.applatefeeamt + flatefee
                    loanmast.status = "C"
                    loanmast.apploansettlementdate = loginrundate

                    loanmast.save()

                    success=True
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid

                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
                        
                    message = "Loan ID of " + fappname +" / "+ fapploanid + " Settled Succesfully."
                    messages.success(request, message)
                    return HttpResponseRedirect('/loansettlement/')

                else:

                    return render(request, 'admssapp/loansettlement.html' , context)






###########################
#### LOAN SETTLE FINAL ####
###########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanforceclosure(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
            
                if request.method == "POST":

                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y').order_by('bankac')

                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid
                    fapploanamt = loanmast.apploanamt
                    fapploanint = loanmast.apploanint
                    fapploanemi = loanmast.apploanemi
                    fapploanprinbal = loanmast.apploanamt - loanmast.appprinrecamt



                    
                    fapploandate = loanmast.apploandate
                    fapploantenr = loanmast.apploantenr
                    delta = loginrundate - loanmast.apploandate
                    fapploandays = delta.days
                    fappshoplocation = loanmast.appshoplocation
                    fappoccupation =  loanmast.appoccupation
                    fappemifreq = loanmast.appemifreq
                    fapplastemidepdate = loanmast.applastemidepdate
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    floantype =  loanmast.loantype
                    flatefees = loanmast.applatefeeamt


                    fdepamt = 0
                    fcaldepamt = 0
                    fcaldepdate = 0
                    fappbalamt = 0
                    datechk="Y"
                    
                    for a in loanled:
                        fdepamt = fdepamt + a.amount

                        if (loginrundate - fapploandate).days > fapploantenr:
                           if (a.date - fapploandate).days > fapploantenr and datechk=="Y":
                               fcaldepdate = a.date
                               fcaldepamt = fdepamt - a.amount
                               datechk="N"

                           if datechk=="Y":
                               fcaldepdate = a.date
                               fcaldepamt = fdepamt                                    

                        flastdepdate = a.date    

                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt = loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt

                    if loanmast.apptotalrecamt >= (loanmast.apploanamt + loanmast.apploanint):
                        fapptotalrecamt = fapptotaldueamt
                        fapptotalbalamt = 0


                    
                    acurrdueamt = 0
                    afcurrdueamt = 0
                    afexcessint = 0

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
                             #fcaldays = int((delta.days)/30)
                             #fcaldays = fcaldays*30
                            
                           
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

                                    
                                 #rate = Rate.objects.get(days=360, date='2021-10-19')
                                 #frate = rate.rate
                                 
                             elif loanmast.apploandate >= datetime.strptime('2021-10-20', '%Y-%m-%d').date():

                                 if fcaldays > 30 and fcaldays <= 60:
                                    fcaldays = 60

                                 elif fcaldays > 60 and fcaldays <= 90:
                                    fcaldays = 90

                                 elif fcaldays > 90 and fcaldays <= 120:
                                    fcaldays = 120

                                 elif fcaldays > 120 and fcaldays <= 150:
                                    fcaldays = 150

                                 elif fcaldays > 150 and fcaldays <= 180:
                                    fcaldays = 180

                                 elif fcaldays > 180 and fcaldays <= 210:
                                    fcaldays = 210

                                 elif fcaldays > 210 and fcaldays <= 240:
                                    fcaldays = 240

                                 elif fcaldays > 240 and fcaldays <= 270:
                                    fcaldays = 270

                                 elif fcaldays > 270 and fcaldays <= 300:
                                    fcaldays = 300

                                 elif fcaldays > 300:
                                    fcaldays = 334

                             
                             nint = (fapploanamt*(frate))/100
                             fint = round((nint*fcaldays)/180)
                             
                             #totaldays = (loginrundate - loanmast.apploandate).days
                             currdueamt = fapploanamt+fint
                             fcurrdueamt = fapploanamt+fint-fapptotalrecamt
                             fexcessint = fint - fapploanint 
                             
                        totaldays = (loginrundate - loanmast.apploandate).days
                        ftotalemidue = round(float(loanmast.apploantenr/7), 2)
                    
                        fcurremidue = round(float(totaldays/7), 2)


                        
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
                        else:
                            ftenuoverdue = round(float(0), 2)

                        if fcurrdueamt > fapptotalbalamt:
                            fminamt = afcurrdueamt
                        else:
                            fminamt = fcurrdueamt
                            
                        foverdueamt = int(fcurremibal * (loanmast.apploanamt/1000) * 7)

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
                        #currdueamt = fapploanamt+fint
                        #fcurrdueamt = fapploanamt+fint-fapptotalrecamt
                        #fexcessint = fint - fapploanint 
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
                            
                        foverdueamt = int(fcurremibal * (loanmast.apploanamt/1000) * 7)

                    ftotaldueamt = fcurrdueamt + foverdueamt - flatefees
                    
                    if fcurrdueamt > fapptotalbalamt:
                        fminamt = afcurrdueamt
                    else:
                        fminamt = fcurrdueamt


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapptotalbalamt':fapptotalbalamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fint':fint,
                            'fminamt':fminamt,
                            'fappbalamt':fappbalamt,
                            'fexcessint':fexcessint,
                            'afexcessint':afexcessint,
                            'fcurrdueamt':fcurrdueamt,
                            'afcurrdueamt':afcurrdueamt,
                            'ftotaldueamt':ftotaldueamt,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'fapploanprinbal':fapploanprinbal,
                            'allbank': allbank,
                            
                        }

                    return render(request, 'admssapp/loanforceclosurecommit.html' , context)
            
                else:

                    return render(request, 'admssapp/loanforceclosure.html' , context)

                    

 


######################################
#### LOAN FORCE SETTLEMENT COMMIT ####
######################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanforceclosurecommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec =  int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode')
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')

                    flatefee = int(request.POST.get('latefee'))






                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname
                    fmasterid = loanmast.id
                    floantype = loanmast.loantype


                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt


                    fapploanprinbal = loanmast.apploanamt - loanmast.appprinrecamt
                    fprinamt = fapploanprinbal

                    fintamt = fcashrec - flatefee 


                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'


                    if flatefee <= 0:
                        flatefee = 0


                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 

                    ####  TRANSNUM  ####

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                    fcashrecemi = int(fcashrec) - int(flatefee)

                    remquo = divmod(fcashrecemi,fapploanemi)
                    multi = remquo[0]
                    remain = remquo[1]

                    #finstno = loanmast.instno + multi
                    #loanmast.instno = loanmast.instno + multi
                    loanmast.applastemidepdate = loginrundate


                    trans = Transcd.objects.get(transcd=femiprintranscd)
                    ftrans = trans.id

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id
                    
                    if fprinamt > 0:    
                        db1 = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=femiprintranscd,transnm=femiprintransnm,
                            mode=fmode,personcode=fpersoncode,personname=fpersonname,
                            loanid=fapploanid ,appname=fappname,
                            bankac=fappbankac,
                            narration=fnarr1,amount=fprinamt,drcr="C",
                            trans_id = ftrans,
                            clcashbank_id = opclid
                            )
            
                        db1.save()


                    trans = Transcd.objects.get(transcd=femiinttranscd)
                    ftrans = trans.id


                    if fintamt > 0: 
                                db2 = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,
                                        transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                        mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                        loanid=fapploanid ,appname=fappname,
                                        bankac=fappbankac,
                                        narration=fnarr2,amount=fintamt,drcr="C",
                                        trans_id = ftrans,
                                        clcashbank_id = opclid
                                        )

                                db2.save()      


                    trans = Transcd.objects.get(transcd=flatefeetranscd)
                    ftrans = trans.id


                    if flatefee > 0:
                                db3 = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,
                                    transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    loanid=fapploanid ,appname=fappname,
                                    bankac=fappbankac,
                                    narration=fnarr3,amount=flatefee,drcr="C",
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )

                                db3.save()
                    

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    if fintamt > 0:
                        fhqamt=fintamt*(mperc/100)
                        facamt=fintamt-fhqamt
                        for all in allcash:

                                all.hqamt = all.hqamt + fhqamt
                                all.acamt = all.acamt + facamt 

                                all.save()
            
            
                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        for all in allcash:
                            all.clcash = all.clcash + int(fcashrec) 
                            all.save()

                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            trans = Transcd.objects.get(transcd=allbank.bankcode)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            opclid = allbank.id
                        

                            fnarr="EMI DEPOSIT/"+fappname.strip()+"/"+fapploanid
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname = loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )
                            db.save()             

                    
                    if int(fcashrec) > 0:

                        lt = Loantrans(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        loanid=fapploanid,
                                        transid=ftransid,duedate=fappemiduedate,
                                        date=loginrundate,delaydays=(delta.days),
                                        amount=fcashrec-flatefee,prinamt=fprinamt,
                                        intamt=fintamt,latefee=flatefee,mode=fmode,
                                        drcr="C",master_id=fmasterid)
                                    
                        lt.save()


                    loanmast.apptotalrecamt = loanmast.apptotalrecamt + int(fcashrec)-int(flatefee)
                    loanmast.appprinrecamt = loanmast.appprinrecamt + fprinamt
                    loanmast.appintrecamt = loanmast.appintrecamt + fintamt
                    loanmast.applatefeeamt = loanmast.applatefeeamt + flatefee
                    loanmast.status = "C"
                    loanmast.apploansettlementdate = loginrundate

                    loanmast.save()

                    success=True
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid

                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
                        
                    message = "Loan ID of " + fappname +" / "+ fapploanid + " Force Closure Succesfully."
                    messages.success(request, message)
                    return HttpResponseRedirect('/loanforceclosure/')

                else:

                    return render(request, 'admssapp/loanforceclosure.html' , context)







###############################
#### LOAN INSURANACE CLAIM ####
###############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loaninsurclaim(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
            
                if request.method == "POST":

                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    #loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    #loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y').order_by('bankac')

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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    famount = loanmast.apploanamt



                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt
                    


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapptotalbalamt':fapptotalbalamt,
                            'famount':famount,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'allbank':allbank,
                            }

                    return render(request, 'admssapp/loaninsurclaimshow.html' , context)
            
                else:
                    return render(request, 'admssapp/loaninsurclaim.html' , context)


 

#####################################
#### LOAN INSURANCE CLAIM COMMIT ####
#####################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loaninsurclaimcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec =  request.POST.get('cashrec')
                    fmode = request.POST.get('emimode')
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fdeathdate = request.POST.get('deathdate')

                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname
                    fmasterid = loanmast.id
                    floantype = loanmast.loantype

                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt


                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt


            
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
               

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'
                    
                    finccliamcd = '3375'
                    finccliamnm = 'LOAN INSURANCE CLAIM'


                    fbalintamt = loanmast.apploanint-loanmast.appintrecamt
                    fbalprinamt = loanmast.apploanamt-loanmast.appprinrecamt 

                    famount = int(fcashrec)

                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr = finccliamnm+"/"+fappname.strip()+"/"+fapploanid 


                    ####  TRANSNUM  ####

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
            
                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        trans = Transcd.objects.get(transcd=finccliamcd)
                        ftrans = trans.id

                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                        opclid = allcash.id

                        if int(fcashrec) > 0:    
                           db = Daybook(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,transid=ftransid,
                                         transcd=finccliamcd,transnm=finccliamnm,
                                         mode=fmode,
                                         loanid=fapploanid ,appname=fappname,
                                         narration=fnarr,amount=int(fcashrec),drcr="C",
                                         trans_id = ftrans,
                                         clcashbank_id = opclid
                                         )
            
                           db1.save()
        
                        for all in allcash:
                            all.clcash = all.clcash + int(fcashrec) 
                            all.save()
                            
                            

                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            trans = Transcd.objects.get(transcd=allbank.bankcode)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            opclid = allbank.id
                            clcashbank_id = opclid

                            fnarr="LOAN INSURANCE CLAIM/"+fappname.strip()+"/"+fapploanid
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname = loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                      )
                            db.save()             


                    loanmast.status = "C"
                    loanmast.apploansettlementdate = loginrundate
                    loanmast.applifeinsurclaim = 'Y'
                    loanmast.applifeinsurclaimmode = fmode
                    loanmast.applifeinsurclaimdate = loginrundate
                    loanmast.appdeathdate = fdeathdate
                    loanmast.applifeinsurclaimamount = int(fcashrec)
                    

                    loanmast.save()

                    success=True
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid

                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
                        
                    message = "Loan Insurance Claim of " + fappname +" / "+ fapploanid + " Processed Succesfully."
                    messages.success(request, message)
                    return HttpResponseRedirect('/loaninsurclaim/')



#######################################
#### LOAN INSURANACE FUND RECEIVED ####
#######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loaninsurfundreceive(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(status="A").order_by('loanid','apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
            
                if request.method == "POST":

                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(loanid=fapploanid)

                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y').order_by('bankac')

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
                    fappemiduedate = loanmast.appemiduedate
                    fappoccupation = loanmast.appoccupation
                    fappshopadd = loanmast.appshopadd
                    fappshoplocation = loanmast.appshoplocation
                    famount = loanmast.apploanamt



                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt
                    


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapptotalbalamt':fapptotalbalamt,
                            'famount':famount,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'allbank':allbank,
                            }

                    return render(request, 'admssapp/loaninsurfundreceiveshow.html' , context)
            
                else:
                    return render(request, 'admssapp/loaninsurfundreceive.html' , context)

 

#############################################
#### LOAN INSURANCE FUND RECEIVED COMMIT ####
#############################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loaninsurfundreceivecommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec =  request.POST.get('cashrec')
                    fmode = request.POST.get('emimode')
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fdeathdate = request.POST.get('deathdate')

                    loanmast = Loanmaster.objects.get(loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')


                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid


            
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
               

                    famount = int(fcashrec)

                    ####  TRANSNUM  ####

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
            
                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        trans = Transcd.objects.get(transcd=finccliamcd)
                        ftrans = trans.id

                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                        opclid = allcash.id

                        if int(fcashrec) > 0:    
                           db = Daybook(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,transid=ftransid,
                                         transcd=finccliamcd,transnm=finccliamnm,
                                         mode=fmode,
                                         loanid=fapploanid ,appname=fappname,
                                         narration=fnarr,amount=int(fcashrec),drcr="C",
                                         trans_id = ftrans,
                                         clcashbank_id = opclid
                                         )
            
                           db1.save()
        
                        for all in allcash:
                            all.clcash = all.clcash + int(fcashrec) 
                            all.save()
                            
                            

                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            trans = Transcd.objects.get(transcd=allbank.bankcode)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            opclid = allbank.id
                            clcashbank_id = opclid

                            fnarr="LOAN INSURANCE FUND RECEIVED/"+fappname.strip()+"/"+fapploanid
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname = loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                      )
                            db.save()             


                    loanmast.appdeathdate = fdeathdate
                    loanmast.applifeinsurclaimamount = int(fcashrec)
                    
                    loanmast.save()

                    success=True
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid

                    nname = Loanmaster.objects.filter(status="A").order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(status="A").order_by('loanid','apploandate')
                        
                    message = "Loan Insurance Fund Received of " + fappname +" / "+ fapploanid + " Processed Succesfully."
                    messages.success(request, message)
                    return HttpResponseRedirect('/loaninsurclaim/')




#####################
#### LOAN MASTER ####
#####################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanmaster(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
             return HttpResponseRedirect('/login')
         else:   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode).order_by('appname','-apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode).order_by('loanid','apploandate')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'nname':nname,
                        'loginstatus':loginstatus,
                        'nloanid':nloanid,
                        'currdate':currdate,
                        }


                if request.method == "POST":  
            
                    fapploanid = request.POST.get('loanidname')
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

                    fstatus = loanmast.status
                    if fstatus == "A":
                        fstatus = "Active"
                        delta = loginrundate - loanmast.apploandate

                    elif fstatus == "C":
                        fstatus = "Closed"
                        delta = loanmast.apploansettlementdate - loanmast.apploandate


                    if loanmast.appemifreq == 'DAILY':
                        emifreqdays = 1
                    elif loanmast.appemifreq == 'WEEKLY':
                        emifreqdays = 7
                    elif loanmast.appemifreq == 'FORTNIGHTLY':
                        emifreqdays = 15
                    elif loanmast.appemifreq == 'MONTHLY':
                        emifreqdays = 30

                    fappname = loanmast.appname
                    fappmobileno = loanmast.appmobileno 
                    fapploanid = loanmast.loanid
                    fapploanamt = loanmast.apploanamt
                    fapploandate = loanmast.apploandate
                    fapploantenr = loanmast.apploantenr
                    fapploanemi = loanmast.apploanemi
                    
                    fapploandays = delta.days
                    fappshoplocation = loanmast.appshoplocation
                    fappoccupation =  loanmast.appoccupation
                    fapploansettlementdate = loanmast.apploansettlementdate
                    fapppresentadd = loanmast.apppresentadd
                    fapppresentaddlandmark = loanmast.apppresentaddlandmark
                    fapppresentaddcity = loanmast.apppresentaddcity
                    fapppresentaddpin = loanmast.apppresentaddpin
                    fapppermanentadd = loanmast.apppermanentadd
                    fapppermanentaddcity = loanmast.apppermanentaddcity
                    fapppermanentaddpin = loanmast.apppermanentaddpin
                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapplastemidepdate = loanmast.applastemidepdate
                    fcoappname = loanmast.coappname
                    fcoapprelation = loanmast.coapprelation
                    fcoappmobileno = loanmast.coappmobileno 
                    fguarname = loanmast.guarname
                    fguarmobileno = loanmast.guarmobileno
                    fguarrelation = loanmast.guarrelation
                    fguarpresentadd = loanmast.guarpresentadd
                    fguarpresentaddcity = loanmast.guarpresentaddcity
                    fguarpresentaddpin = loanmast.guarpresentaddpin
                    fguaroccupation = loanmast.guaroccupation
                    floantype = loanmast.loantype
                    fappshopadd = loanmast.appshopadd
                    fapploanint = loanmast.apploanint
                    fapptotalbalamt = loanmast.apploanbalamt
                    fapplifeinsurdate = loanmast.applifeinsurdate
                    fapplifeinsuruptodate = loanmast.applifeinsuruptodate
                    frpersonname = loanmast.rpersonname
                    fassociatename = loanmast.associatename
                    fadminpersonname = loanmast.adminpersonname
                    fcolldaychar = loanmast.colldaychar
                    fappemifreq = loanmast.appemifreq
                    flatefees = loanledsumm1.get("totlatefee")

                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                    # fcaldepamt = 0
                    fdepamt = 0
                    datechk="Y"
                    for a in loanled:
                        fdepamt = fdepamt + a.amount

                        if (loginrundate - fapploandate).days > fapploantenr:
                           if (a.date - fapploandate).days > fapploantenr and datechk=="Y":
                               fcaldepdate = a.date
                               fcaldepamt = fdepamt - a.amount
                               datechk="N"


                           if datechk=="Y":
                               fcaldepdate = a.date
                               fcaldepamt = fdepamt                                    

                        flastdepdate = a.date   

                    fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                    totaldays = (loginrundate - loanmast.apploandate).days
                    currdueamt = fapploanamt+fint
                    fcurrdueamt = fapploanamt+fint-fapptotalrecamt
                    fexcessint = fint - fapploanint 
                    ftotalemidue = round(float(loanmast.apploantenr/emifreqdays), 2)
                    fcurremidue = round(float(totaldays/emifreqdays), 2)
                    if fcurremidue > ftotalemidue:
                        fcurremidue = ftotalemidue
                    fcurremidone = round(float(loanmast.apptotalrecamt/loanmast.apploanemi), 2)
                    fcurremibal = round(float(fcurremidue - fcurremidone), 2)
                    if fcurremibal < 0:
                        fcurremibal = 0
                    fcurroverdue =  int(fcurremibal*loanmast.apploanemi)
                    if totaldays >= loanmast.apploantenr:
                        tenuoverdue =  totaldays - loanmast.apploantenr
                        ftenuoverdue = round(float(tenuoverdue/emifreqdays), 2)
                    else:
                        ftenuoverdue = round(float(0), 2)


                    foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                    ftotaldueamt = fcurrdueamt + foverdueamt - flatefees
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))                    
                    latefee = int((loanmast.apploanamt/1000) * fdelaydays)  

                    if loanmast.status == 'C':
                        fdelaydays=0
                        foverdueamt=0
                        totaldelaydays=0
                        foverdueamt=0
                        fdelaydays=0
                        latefee=0



                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'loanled':loanled,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fstatus':fstatus,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fstatus':fstatus,
                            'fapploandays':fapploandays,
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fapploansettlementdate':fapploansettlementdate,
                            'fapppresentadd':fapppresentadd,
                            'fapppresentaddlandmark':fapppresentaddlandmark,
                            'fapppresentaddcity':fapppresentaddcity,
                            'fapppresentaddpin':fapppresentaddpin,
                            'fappmobileno':fappmobileno,
                            'fcoappmobileno':fcoappmobileno,
                            'fapppermanentadd':fapppresentadd,
                            'fapppermanentaddcity':fapppermanentaddcity,
                            'fapppermanentaddpin':fapppermanentaddpin,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fcoappname':fcoappname,
                            'fcoapprelation':fcoapprelation,
                            'fguarname':fguarname,
                            'fguarmobileno':fguarmobileno,
                            'fguarrelation':fguarrelation,
                            'fguarpresentadd':fguarpresentadd,
                            'fguarpresentaddcity':fguarpresentaddcity,
                            'fguarpresentaddpin':fguarpresentaddpin,
                            'fguaroccupation':fguaroccupation,
                            'fappshopadd':fappshopadd,
                            'fapplifeinsurdate':fapplifeinsurdate,
                            'fapplifeinsuruptodate':fapplifeinsuruptodate,
                            'frpersonname':frpersonname,
                            'fassociatename':fassociatename,
                            'fadminpersonname':fadminpersonname,
                            'fcolldaychar':fcolldaychar,
                            'loanledsumm':loanledsumm,
                            'ftotalemidue':ftotalemidue,
                            'fappemifreq':fappemifreq,
                            'fcurremidue':fcurremidue,
                            'fcurremidone':fcurremidone,
                            'fdelaydays':fdelaydays,
                            'foverdueamt':foverdueamt,
                            'ftotaldueamt':ftotaldueamt,
                            'fcurroverdue':fcurroverdue,
                            'fcurremibal':fcurremibal,
                            'totaldelaydays':totaldelaydays,
                            'fdelaydays':fdelaydays,
                            'latefee':latefee,

                                }

            
                    if request.method == "POST" and "show" in request.POST:

                        return render(request, 'admssapp/loanmastershow.html' , context)

                    if request.method == "POST" and "pdf" in request.POST:

                        pdf = render_to_pdf('admssapp/loanmasterpdf.html', context)
                        return HttpResponse(pdf, content_type='application/pdf')
                else:

                        return render(request, 'admssapp/loanmaster.html' , context)




###################################################
################### Name Search ###################
###################################################

import json

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def masterautocomplete(request):
    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
        
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    
    results = []
    
    if is_ajax(request=request):
        q = request.GET.get('term', '').capitalize()


        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,appname__icontains=request.GET.get('term', '').capitalize()).order_by('appname')

        for r in search_qs:
            results.append(r.appname + '/' + r.appshoplocation +'/' +r.loanid)

        data = json.dumps(results)
    else:
        data = json.dumps(results)
        q = 'pain'
        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,appname__icontains=request.GET.get('term', '').capitalize())


        for r in search_qs:
            results.append(r.appname +'/' + r.appshoplocation +'/' + r.loanid)

        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)




############################
#### LOAN MASTER UPDATE ####
############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def updatemaster(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
             return HttpResponseRedirect('/login')
         else:
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }


                if request.method == "POST":  
            
                    fapploanid = request.POST.get('loanidname')
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid)
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    allcoll = Personmaster.objects.filter(locationcode=loginlocationcode,persontype='COLL').distinct().order_by('personname')

                    alladmin = Personmaster.objects.filter(locationcode=loginlocationcode, admin='Y').distinct().order_by('personname')

                    frpersonname = loanmast.rpersonname
                    fappemiduedate = loanmast.appemiduedate
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid

                    fapploandate = loanmast.apploandate
                    fapploantenr = loanmast.apploantenr
                    fappshoplocation = loanmast.appshoplocation
                    fappshopadd = loanmast.appshopadd
                    fappoccupation =  loanmast.appoccupation
                    fapploansettlementdate = loanmast.apploansettlementdate
                    fapppresentadd = loanmast.apppresentadd
                    fapppresentaddlandmark = loanmast.apppresentaddlandmark
                    fapppresentaddcity = loanmast.apppresentaddcity
                    fapppresentaddpin = loanmast.apppresentaddpin
                    fapppermanentadd = loanmast.apppermanentadd
                    fapppermanentaddcity = loanmast.apppermanentaddcity
                    fapppermanentaddpin = loanmast.apppermanentaddpin
                    floantype = loanmast.loantype
                    fappemiduedate = loanmast.appemiduedate
                    frpersoncode = loanmast.rpersoncode
                    frpersonname = loanmast.rpersonname
                    fadminpersoncode = loanmast.adminpersoncode
                    fadminpersonname = loanmast.adminpersonname                    
                    fappmobno = loanmast.appmobileno
                    fcoappmobno = loanmast.coappmobileno
                    fguarmobno = loanmast.guarmobileno
                    fguarname = loanmast.guarname                    
                    fpassbookno = loanmast.passbookno
                    fguardob = loanmast.guardob
                    fguargender = loanmast.guargender
                    fcoappname = loanmast.coappname  
                    fcoapprelation = loanmast.coapprelation
                    fcoappgender = loanmast.coappgender
                    fcoappadhar = loanmast.coappadharno


                    if fguardob is None:
                        fguardob = '1970-01-01'
                    else:
                        fguardob = loanmast.guardob.strftime("%Y-%m-%d")    

                    if fcoappadhar is None:
                        fcoappadhar = ''


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'loanled':loanled,
                            'allcoll':allcoll,
                            'alladmin':alladmin,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapploandate':fapploandate,
                            'fappshoplocation':fappshoplocation,
                            'fappshopadd':fappshopadd,
                            'fappoccupation':fappoccupation,
                            'fapploansettlementdate':fapploansettlementdate,
                            'fapppresentadd':fapppresentadd,
                            'fapppresentaddlandmark':fapppresentaddlandmark,
                            'fapppresentaddcity':fapppresentaddcity,
                            'fapppresentaddpin':fapppresentaddpin,
                            'fappemiduedate':fappemiduedate,
                            'frpersonname':frpersonname,
                            'fadminpersonname':fadminpersonname,
                            'fappmobno':fappmobno,
                            'fcoappmobno':fcoappmobno,
                            'fguarmobno':fguarmobno,
                            'fpassbookno': fpassbookno,
                            'fguardob':fguardob,
                            'fguargender':fguargender,
                            'fguarname':fguarname,
                            'fcoappname':fcoappname,
                            'fcoapprelation':fcoapprelation,
                            'fcoappgender':fcoappgender,
                            'fcoappadhar':fcoappadhar,

                            }


                    return render(request, 'admssapp/updatemastershow.html' , context)

                else:

                    return render(request, 'admssapp/updatemaster.html' , context)



###################################
#### LOAN MASTER UPDATE COMMIT ####
###################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def updatemastercommit(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
  

                if request.method == "POST":  
            
                    fapploanid = request.POST.get('loanidname')
                    fdefaultemiduedate = request.POST.get('defaultemiduedate')
                    fdefaultrperson = request.POST.get('defaultrperson')
                    fdefaultadmin = request.POST.get('defaultadmin')

                    fadmincode = request.POST.get('admincode')
                    frpersoncode = request.POST.get('rpersoncode')
                    femiduedate = request.POST.get('emiduedate')

                    fdefaultpassbook = request.POST.get('defaultpassbook')
                    fpassbookno = request.POST.get('passbookno')

                    fdefaultappmobno = request.POST.get('defaultappmobno')
                    fappmobileno = request.POST.get('appmobileno')

                    defaultcoappmobno = request.POST.get('defaultcoappmobno')
                    fcoappmobileno = request.POST.get('coappmobileno')

                    defaultguarmobno = request.POST.get('defaultguarmobno')
                    fguarmobileno = request.POST.get('guarmobileno')

                    defaultguargender = request.POST.get('defaultguargender')
                    fguargender = request.POST.get('guargender')

                    defaultguardob = request.POST.get('defaultguardob')
                    fguardob = request.POST.get('guardob')

                    defaultcoappgender = request.POST.get('defaultcoappgender')
                    fcoappgender = request.POST.get('coappgender')

                    defaultcoappadhaar = request.POST.get('defaultcoappadhaar')
                    fcoappadhar = request.POST.get('coappadhar')


                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    fapploanid = loanmast.loanid
                    fappname = loanmast.appname
            
                    narr1=""
                    narr2=""
                    narr3=""
                    narr4=""
                    narr5=""
                    narr6=""
                    narr7=""
                    narr8=""
                    narr9=""
                    narr10=""

                    if fdefaultemiduedate == "on":
                        loanmast.appemiduedate = femiduedate
                        
                        colldaychar = datetime.strptime(femiduedate, "%Y-%m-%d").strftime('%A')
                        colldaynum = datetime.strptime(femiduedate, "%Y-%m-%d").strftime('%w')
                        
                        loanmast.colldaychar = colldaychar
                        loanmast.colldaynum = colldaynum

                        narr1 = "Emi Due Date Modified as " + femiduedate

                    if fdefaultrperson == "on":
                        personmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode= frpersoncode)
                        loanmast.rpersoncode = personmast.personcode
                        loanmast.rpersonname = personmast.personname
                        narr2 = "Emi Collectot Modified as " + personmast.personname

                    if fdefaultadmin == "on":
                        personmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode= fadmincode)
                        loanmast.adminpersoncode = personmast.personcode
                        loanmast.adminpersonname = personmast.personname
                        narr2 = "Admin Modified as " + personmast.personname

                    if fdefaultappmobno == "on":
                        loanmast.appmobileno = fappmobileno

                        narr3 = "Applicant Mobile No. modified as " +  loanmast.appmobileno

                    if defaultcoappmobno == "on":
                        loanmast.coappmobileno = fcoappmobileno

                        narr4 = "Coapplicant Mobile No. modified as " +  loanmast.coappmobileno


                    if defaultguarmobno == "on":
                        loanmast.guarmobileno = fguarmobileno

                        narr5 = "Guaranter Mobile No. modified as " +  loanmast.guarmobileno

                    if fdefaultpassbook == "on":
                        loanmast.passbookno = fpassbookno

                        narr6 = "Applicant Passbook No. modified as " +  loanmast.passbookno

                    if defaultguargender == "on":
                        loanmast.guargender = fguargender

                        narr7 = "Guarantor gender modified as " +  loanmast.guargender

                    if defaultguardob == "on":
                        loanmast.guardob = fguardob

                        narr8 = "Guarantor DOB modified as " +  loanmast.guardob

                    if defaultcoappgender == "on":
                        loanmast.coappgender = fcoappgender

                        narr9 = "Coapplicant Gender modified as " +  loanmast.coappgender

                    if defaultcoappadhaar == "on":
                        loanmast.coappadharno = fcoappadhar

                        narr10 = "Coapplicant adhaar modified as " +  loanmast.coappadharno


                    loanmast.save()
                    
                    success = True
                    narr = fapploanid+"/"+fappname+" "+narr1+" "+narr2 +" "+ narr3 +" "+ narr4 +" "+ narr5 +" " + narr6 +" " + narr7 + " " + narr8 + " " + narr9 + " " + narr10

                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('loanid','apploandate')

                    context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,     
                        'nname':nname,
                        'nloanid':nloanid,
                        'success':True,
                        'narr':narr,
                         }
                    return render(request, 'admssapp/updatemaster.html' , context)

                else:

                    return render(request, 'admssapp/updatemaster.html' , context)





############################
####  NOC CERTIFICATES  ####
############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def noccertificate(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
  
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='C').order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='C').order_by('loanid', 'apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }


                if request.method == "POST":  
            
                    fapploanid = request.POST.get('loanidname')
        
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
        

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate': currdate,
                            'loanmast':loanmast,
                            }

                    return render(request, 'admssapp/nocshow.html' , context)

                else:
                        return render(request, 'admssapp/noc.html' , context)



#################################
####### EMI CALCULATE ###########
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emicalculator(request):
                loguserid = request.session['loguserid']
                ll=Locationlogin.objects.get(user=loguserid)
        
                loginlocationcode=ll.locationcode
                loginlocationname=ll.locationname
                loginrundate=ll.rundate
                loginstatus = ll.status
                currdate = date.today()


                user = User.objects.get(id=loguserid)
                if user is not None and loginstatus not in(['B','A']):
                    return HttpResponseRedirect('/login')
                else:
        
                        rate = Rate.objects.all().order_by('days')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate': currdate,
                                'rate':rate,
                                }


                        if request.method == "POST":
                            famount = request.POST.get('amount')
                            amount = int(famount)
                            fdays = request.POST.get('days')
                            ndays = int(fdays)

                            rate = Rate.objects.get(days=365,date='2021-10-20')
                            frate = rate.rate

                            nint=round((amount*(frate))/100)

                            fint=int((nint*ndays)/180)

                            total = amount+fint

                            daycoll = round((total/ndays),2)
                            weekcoll = round((daycoll*7),2)


                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate': currdate,
                                    'rate':rate,
                                    'total':total,
                                    'daycoll':daycoll,
                                    'weekcoll':weekcoll,
                                    'famount':famount,
                                    'total':total,
                                    'fdays':fdays,
                                    }
                            return render(request, 'admssapp/emicalculateshow.html' , context)

                        return render(request, 'admssapp/emicalculate.html' , context)



##################################
########## EMI DEPOSIT ###########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emideposit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        'success':False,
                        }

                
            
                if request.method == "POST":
                    
                        fapploanid = request.POST.get('loanidname')

                        loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                        loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                        loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                        fapploanid = loanmast.loanid

                        fappname = loanmast.appname
                        fapploanemi = loanmast.apploanemi
                        fapplastemidepdate = loanmast.applastemidepdate
                        fapplastemidepday = ''
                        if fapplastemidepdate is not None:
                            fapplastemidepday = loanmast.applastemidepdate.strftime('%A')


                        fappemiduedate = loanmast.appemiduedate
                        fapptotalrecamt = loanmast.apptotalrecamt
                        fapploanamt = loanmast.apploanamt
                        fappoccupation = loanmast.appoccupation
                        fappshoplocation = loanmast.appshoplocation
                        frpersoncode = loanmast.rpersoncode
                        frpersonname = loanmast.rpersonname
                        femiday = loanmast.colldaychar

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname
                    
                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)     
                        flatefees = loanledsumm1.get("totlatefee")

                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                        fapptotalrecamt = loanmast.apptotalrecamt
                        fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                        fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)                          

                        acurrdueamt = 0
                        afcurrdueamt = 0
                        afexcessint = 0
                    
                        fappbalamt = 0
         
                
                        fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                        foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                        ftotaldueamt = fcurrdueamt + foverdueamt - flatefees                   

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                        allcoll = Personmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(persontype='COLL') & ~Q(personcode = frpersoncode)).distinct().order_by('personname')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'fapploanid':fapploanid,
                                'fappname':fappname,
                                'fapploanemi':fapploanemi,
                                'fapploanamt':fapploanamt,
                                'fapplastemidepdate':fapplastemidepdate,
                                'fapplastemidepday':fapplastemidepday,
                                'fappemiduedate':fappemiduedate,
                                'fapptotalrecamt':fapptotalrecamt,
                                'allbank':allbank,
                                'fdelaydays':fdelaydays,
                                'latefee':latefee,
                                'fappoccupation':fappoccupation,
                                'fappshoplocation':fappshoplocation,
                                'frpersoncode':frpersoncode,
                                'frpersonname':frpersonname,
                                'femiday':femiday,
                                'allcoll':allcoll,
                                'fcurremidue':fcurremidue,
                                'fcurremidone':fcurremidone,
                                'fcurroverdue':fcurroverdue,
                                 }
                        
                        return render(request, 'admssapp/emiprocess.html' , context)
                    
                else:

                    return render(request, 'admssapp/emideposit.html' , context)



###################################################
################### Name Search ###################
###################################################

import json

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def autocomplete(request):
    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
        
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    
    results = []
    
    if is_ajax(request=request):
        q = request.GET.get('term', '').capitalize()


        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',appname__icontains=request.GET.get('term', '').capitalize()).order_by('appname')

        for r in search_qs:
            results.append(r.appname + '/' + r.appshoplocation +'/' +r.loanid)

        data = json.dumps(results)
    else:
        data = json.dumps(results)
        q = 'pain'
        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',appname__icontains=request.GET.get('term', '').capitalize())


        for r in search_qs:
            results.append(r.appname +'/' + r.appshoplocation +'/' + r.loanid)

        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


#######################################################
################### Name Search NOC ###################
#######################################################

import json

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def autocompletenoc(request):
    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
        
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    
    results = []
    
    if is_ajax(request=request):
        q = request.GET.get('term', '').capitalize()


        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,status='C',appname__icontains=request.GET.get('term', '').capitalize()).order_by('appname','-id')

        for r in search_qs:
            results.append(r.appname + '/' + r.appshoplocation +'/' +r.loanid)

        data = json.dumps(results)
    else:
        data = json.dumps(results)
        q = 'pain'
        search_qs = Loanmaster.objects.filter(locationcode=loginlocationcode,status='C',appname__icontains=request.GET.get('term', '').capitalize())


        for r in search_qs:
            results.append(r.appname +'/' + r.appshoplocation +'/' + r.loanid)

        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


###################################
########### EMI COMMIT ############
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emicommit(request):
     
    #if request.user.is_authenticated:
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec=0
                    
                    if len(request.POST.get('cashrec'))>0:
                        fcashrec = int(request.POST.get('cashrec'))

                    flatefee=0
                    if len(request.POST.get('latefee'))>0:   
                        flatefee = int(request.POST.get('latefee'))

                    fnewrpersoncode = request.POST.get('newrpersoncode')

                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')

                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
            
                    fmasterid = loanmast.id
                    fapploanid = loanmast.loanid
                    fappname = loanmast.appname
                    fapploanemi = loanmast.apploanemi
                    fapploanemiprin = loanmast.apploanemiprin
                    fapploanemiint = loanmast.apploanemiint
                    fappemiduedate = loanmast.appemiduedate
                    fapploanamt = loanmast.apploanamt

                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname

                    if fnewrpersoncode:
                        newrperson = Personmaster.objects.get(locationcode = loginlocationcode, personcode = fnewrpersoncode)
                        fpersoncode = newrperson.personcode
                        fpersonname = newrperson.personname

                    
                    fapploanemi,fapploanemiprin,fapploanemiint,fapploanint = updateamount(fapploanid, loginlocationcode, loginrundate)



                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'


                    fcashrecemi = fcashrec - flatefee

                    #### Delay Days #### 

                    delta=loginrundate-fappemiduedate

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    ####  TRANSNUM  ####
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            


                    remquo = divmod(fcashrecemi,fapploanemi)
                    multi = remquo[0]
                    remain = remquo[1]

    
                    if multi > 0:
                        if loanmast.appemifreq == "DAILY":
                            loanmast.appemiduedate = (loanmast.appemiduedate + timedelta(1*multi))


                        elif loanmast.appemifreq == "WEEKLY":
                            loanmast.appemiduedate = (loanmast.appemiduedate + timedelta(7*multi))


                        elif loanmast.appemifreq == "FORTNIGHTLY":

                            loanmast.appemiduedate = loanmast.appemiduedate + timedelta(15*multi)
                            if int(loanmast.appemiduedate.strftime("%d")) >= 15:

                                   if loanmast.appemisecondfn == '  ':
                                       loanmast.appemisecondfn = '20'

                                   fappemiduedate = (loanmast.appemiduedate.strftime("%Y"))+(loanmast.appemiduedate.strftime("%m"))+loanmast.appemisecondfn
                                   fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                     
                            elif int(loanmast.appemiduedate.strftime("%d")) < 15:

                                    if loanmast.appemifirstfn == '  ':
                                       loanmast.appemifirstfn = '05'
                              
                                    fappemiduedate = (loanmast.appemiduedate.strftime("%Y"))+(loanmast.appemiduedate.strftime("%m")) + loanmast.appemifirstfn
                                    fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                            
                            loanmast.appemiduedate = fappemiduedate


                        elif loanmast.appemifreq == "MONTHLY":
                            fappemiduedate = (loanmast.appemiduedate + relativedelta(months=+1))


                    else:
                        loanmast.appemiduedate = loanmast.appemiduedate
                        fappemiduedate =  loanmast.appemiduedate


                    fcolldaychar = loanmast.appemiduedate.strftime('%A')
                    fcolldaynum = loanmast.appemiduedate.strftime('%w')


                    fcashrecemi = fcashrec - flatefee

                    fbalprinamt = loanmast.apploanamt - loanmast.appprinrecamt 
                    fbalintamt = fapploanint - loanmast.appintrecamt

                    if (loanmast.appprinrecamt+loanmast.appintrecamt) >= (loanmast.apploanamt+loanmast.apploanint) :
                        fbalintamt = 0




                    ##########################
                    fintamt = round(fcashrecemi*(fapploanemiint/fapploanemi))
                    fintamt = round(fintamt*.95)
                    ##########################
        
                    if fbalintamt > 0 and fbalintamt <= fintamt:
                        fintamt = fbalintamt
                    elif fbalintamt <= 0:
                        fintamt = 0
                
                    fprinamt = fcashrecemi - fintamt

                    if fbalprinamt <= 0:
                        fprinamt = 0 
                        
                    
                    flatefee = flatefee + (fcashrecemi - fprinamt - fintamt)

                    if flatefee <= 0:
                        flatefee = 0

                    #finstno = loanmast.instno + multi
                    #loanmast.instno = loanmast.instno + multi
                    loanmast.applastemidepdate = loginrundate
                    loanmast.colldaychar = fcolldaychar
                    loanmast.colldaynum = fcolldaynum
                    loanmast.groupemicoll = 'N'
                    loanmast.save()

                
                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 


                    trans = Transcd.objects.get(transcd=femiprintranscd)
                    ftrans = trans.id

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id


                    if fprinamt > 0:            
                        db1 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=femiprintranscd,transnm=femiprintransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr1,amount=fprinamt,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid )
            
                        db1.save()



                    trans = Transcd.objects.get(transcd=femiinttranscd)
                    ftrans = trans.id

                    if fintamt > 0:            
                        db2 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,
                                transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr2,amount=fintamt,drcr="C",
                                trans_id=ftrans,
                                clcashbank_id = opclid
                                )

                        db2.save()      

        
                    trans = Transcd.objects.get(transcd=flatefeetranscd)
                    ftrans = trans.id

                    if flatefee > 0:
                        db3 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,
                                transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr3,amount=flatefee,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid)

                        db3.save()      
            
                    if fintamt > 0:
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        fhqamt=fintamt*(mperc/100)
                        facamt=fintamt-fhqamt
                        for all in allcash:

                                #all.hqamt = all.hqamt + round(fintamt*(mperc/100))
                                all.hqamt = all.hqamt + fhqamt
                                all.acamt = all.acamt + facamt 

                                all.save()


                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        for all in allcash:
                            all.clcash = all.clcash + fcashrec
                            all.save()


                    if fmode == "BANK":

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        opclid = allbank.id


                        trans = Transcd.objects.get(transcd=allbank.bankcode)
                        ftrans = trans.id

 
                        fnarr="EMI DEPOSIT/"+fappname.strip()+"/"+fapploanid
                        db = Daybook(locationcode = flocationcode,
                                    locationname=loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )
                
                        db.save()             
        
                    
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank=allbank.clbank + fcashrec
                        allbank.save()

                    if fcashrec > 0:
                            lt = Loantrans(locationcode=flocationcode,
                                        locationname=loginlocationname,
                                        loanid=fapploanid,
                                        transid=ftransid,duedate=fappemiduedate,
                                        date=loginrundate,delaydays=(delta.days),
                                        amount=fcashrec-flatefee,prinamt=fprinamt,
                                        intamt=fintamt,latefee=flatefee,mode=fmode,
                                        drcr="C",master_id=fmasterid)
                                    
                            lt.save()

                    loanmast.apptotalrecamt = loanmast.apptotalrecamt + (fcashrec-flatefee)
                    loanmast.appprinrecamt = loanmast.appprinrecamt + fprinamt
                    loanmast.appintrecamt = loanmast.appintrecamt + fintamt
                    loanmast.applatefeeamt = loanmast.applatefeeamt + flatefee
                    loanmast.save()


                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')

                    message = "EMI of "+fappname+" / "+fapploanid+" / "+"Rs."+str(fcashrec)+" / Processed Succesfully through "+fmode+" --  "+fpersonname

                    messages.success(request, message)
                    return HttpResponseRedirect('/emideposit/')




##########################################
########## EMI SPECIAL DEPOSIT ###########
##########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emispecialdeposit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        'success':False,
                        }

                
            
                if request.method == "POST":
                    
                        fapploanid = request.POST.get('loanidname')

                        loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                        loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                        loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                        fapploanid = loanmast.loanid

                        fappname = loanmast.appname
                        fapploanemi = loanmast.apploanemi
                        fapplastemidepdate = loanmast.applastemidepdate
                        fapplastemidepday = ''
                        if fapplastemidepdate is not None:
                            fapplastemidepday = loanmast.applastemidepdate.strftime('%A')


                        fappemiduedate = loanmast.appemiduedate
                        fapptotalrecamt = loanmast.apptotalrecamt
                        fapploanamt = loanmast.apploanamt
                        fappoccupation = loanmast.appoccupation
                        fappshoplocation = loanmast.appshoplocation
                        frpersoncode = loanmast.rpersoncode
                        frpersonname = loanmast.rpersonname
                        femiday = loanmast.colldaychar

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        fappname = loanmast.appname
                        fapploanid = loanmast.loanid
                        fapploanamt = loanmast.apploanamt
                        fapploanint = loanmast.apploanint
                        fapploanemi = loanmast.apploanemi

                        fapploanprinbal = loanmast.apploanamt - loanmast.appprinrecamt
                        if fapploanprinbal < 0:
                            fapploanprinbal=0

                        fapploanintbal = loanmast.apploanint - loanmast.appintrecamt

                        if fapploanintbal < 0:
                            fapploanintbal=0


                        ftotaldue = fapploanamt + fapploanint




                    
                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)     
                        flatefees = loanledsumm1.get("totlatefee")

                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                        fapptotalrecamt = loanmast.apptotalrecamt
                        fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                        fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)                          

                        acurrdueamt = 0
                        afcurrdueamt = 0
                        afexcessint = 0
                    
                        fappbalamt = 0
         
                
                        fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                        foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                        ftotaldueamt = fcurrdueamt + foverdueamt - flatefees                   

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                        allcoll = Personmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(persontype='COLL') & ~Q(personcode = frpersoncode)).distinct().order_by('personname')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'fapploanid':fapploanid,
                                'fappname':fappname,
                                'fapploanemi':fapploanemi,
                                'fapploanamt':fapploanamt,
                                'fapplastemidepdate':fapplastemidepdate,
                                'fapplastemidepday':fapplastemidepday,
                                'fappemiduedate':fappemiduedate,
                                'fapptotalrecamt':fapptotalrecamt,
                                'allbank':allbank,
                                'fdelaydays':fdelaydays,
                                'latefee':latefee,
                                'fappoccupation':fappoccupation,
                                'fappshoplocation':fappshoplocation,
                                'frpersoncode':frpersoncode,
                                'frpersonname':frpersonname,
                                'femiday':femiday,
                                'allcoll':allcoll,
                                'fcurremidue':fcurremidue,
                                'fcurremidone':fcurremidone,
                                'fcurroverdue':fcurroverdue,
                                'fapploanprinbal':fapploanprinbal,
                                'fapploanintbal':fapploanintbal,
                                'ftotaldue':ftotaldue,
                                
                                 }
                        
                        return render(request, 'admssapp/emispecialprocess.html' , context)
                    
                else:
                    return render(request, 'admssapp/emispecialdeposit.html' , context)





###########################################
########### EMI SPECIAL COMMIT ############
###########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emispecialtcommit(request):
     
    #if request.user.is_authenticated:
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
        
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                  
                    fcashrec=0
                    if len(request.POST.get('cashrec'))>0:
                        fcashrec = int(request.POST.get('cashrec'))

                    fprinamt=0
                    if len(request.POST.get('prinamt'))>0:   
                        fprinamt = int(request.POST.get('prinamt'))

                    flatefee=0
                    if len(request.POST.get('latefee'))>0:   
                        flatefee = int(request.POST.get('latefee'))

                    fintamt=0
                    fintamt =  fcashrec - fprinamt - flatefee

                    if fintamt < 0:
                        fintamt = 0


                    fnewrpersoncode = request.POST.get('newrpersoncode')

                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')

                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
            
                    fmasterid = loanmast.id
                    fapploanid = loanmast.loanid
                    fappname = loanmast.appname
                    fapploanemi = loanmast.apploanemi
                    fapploanemiprin = loanmast.apploanemiprin
                    fapploanemiint = loanmast.apploanemiint
                    fappemiduedate = loanmast.appemiduedate
                    fapploanamt = loanmast.apploanamt

                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname

                    if fnewrpersoncode:
                        newrperson = Personmaster.objects.get(locationcode = loginlocationcode, personcode = fnewrpersoncode)
                        fpersoncode = newrperson.personcode
                        fpersonname = newrperson.personname


                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'


                    #fcashrecemi = fcashrec - flatefee

                    #### Delay Days #### 

                    delta=loginrundate-fappemiduedate

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                    ####  TRANSNUM  ####
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            


                    if flatefee <= 0:
                        flatefee = 0


                    fcolldaychar = loanmast.appemiduedate.strftime('%A')
                    fcolldaynum = loanmast.appemiduedate.strftime('%w')


                    loanmast.applastemidepdate = loginrundate
                    loanmast.colldaychar = fcolldaychar
                    loanmast.colldaynum = fcolldaynum
                    loanmast.groupemicoll = 'N'
                    loanmast.save()

                
                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 


                    trans = Transcd.objects.get(transcd=femiprintranscd)
                    ftrans = trans.id

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id


                    if fprinamt > 0:            
                        db1 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=femiprintranscd,transnm=femiprintransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr1,amount=fprinamt,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid )
            
                        db1.save()



                    trans = Transcd.objects.get(transcd=femiinttranscd)
                    ftrans = trans.id

                    if fintamt > 0:            
                        db2 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,
                                transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr2,amount=fintamt,drcr="C",
                                trans_id=ftrans,
                                clcashbank_id = opclid
                                )

                        db2.save()      

        
                    trans = Transcd.objects.get(transcd=flatefeetranscd)
                    ftrans = trans.id

                    if flatefee > 0:
                        db3 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,
                                transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr3,amount=flatefee,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid)

                        db3.save()      
            
                    if fintamt > 0:
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        fhqamt=fintamt*(mperc/100)
                        facamt=fintamt-fhqamt
                        for all in allcash:

                                #all.hqamt = all.hqamt + round(fintamt*(mperc/100))
                                all.hqamt = all.hqamt + fhqamt
                                all.acamt = all.acamt + facamt 

                                all.save()


                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        for all in allcash:
                            all.clcash = all.clcash + fcashrec
                            all.save()


                    if fmode == "BANK":

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        opclid = allbank.id


                        trans = Transcd.objects.get(transcd=allbank.bankcode)
                        ftrans = trans.id

 
                        fnarr="EMI DEPOSIT/"+fappname.strip()+"/"+fapploanid
                        db = Daybook(locationcode = flocationcode,
                                    locationname=loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )
                
                        db.save()             
        
                    
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank=allbank.clbank + fcashrec
                        allbank.save()

                    if fcashrec > 0:
                            lt = Loantrans(locationcode=flocationcode,
                                        locationname=loginlocationname,
                                        loanid=fapploanid,
                                        transid=ftransid,duedate=fappemiduedate,
                                        date=loginrundate,delaydays=(delta.days),
                                        amount=fcashrec-flatefee,prinamt=fprinamt,
                                        intamt=fintamt,latefee=flatefee,mode=fmode,
                                        drcr="C",master_id=fmasterid)
                                    
                            lt.save()

                    loanmast.apptotalrecamt = loanmast.apptotalrecamt + (fcashrec-flatefee)
                    loanmast.appprinrecamt = loanmast.appprinrecamt + fprinamt
                    loanmast.appintrecamt = loanmast.appintrecamt + fintamt
                    loanmast.applatefeeamt = loanmast.applatefeeamt + flatefee
                    loanmast.save()


                    nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                    nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')

                    message = "EMI of "+fappname+" / "+fapploanid+" / "+"Rs."+str(fcashrec)+" / Processed Succesfully through "+fmode+" --  "+fpersonname

                    messages.success(request, message)
                    return HttpResponseRedirect('/emispecialdeposit/')





########################################
########## GROUP EMI DEPOSIT ###########
########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemideposit(request):


         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                ngroupname = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A', groupleader='Y', appemiduedate__lte=loginrundate+timedelta(1)).values(
                 'groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')
                ngroupid = Loanmaster.objects.filter(locationcode=loginlocationcode, status='A', groupleader='Y').values(
                    'groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ngroupname': ngroupname,
                        'ngroupid': ngroupid,
                        'success':False,
                        }



                if request.method == "POST" and 'show' in request.POST:
                      
                        fgroupid = request.POST.get('groupidname')

                        groupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid = fgroupid,groupleader='Y')

                        fgroupid =  groupleager.groupid
                        fgroupleadername = groupleager.groupleadername
                        fgrouplocation = groupleager.appshoplocation
                        floanemi = groupleager.apploanemi
                        fgroupemi = groupleager.grouploanemi


                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'fgroupid':fgroupid,
                                'fgroupleadername':fgroupleadername,
                                'fgrouplocation':fgrouplocation,
                                'fgroupemi' : fgroupemi,
                                'floanemi': floanemi,
                                 }
                        
                        return render(request, 'admssapp/groupemidepositget.html', context)


                if request.method == "POST" and 'cancel' in request.POST:
                        fgroupid = request.POST.get('groupidname')
       
                        epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

                        fgroupid =  epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation

 
                        epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'epgrouploan':epgrouploan,
                                'fgroupid':fgroupid,
                                'fgroupleadername':fgroupleadername,
                                'fgrouplocation':fgrouplocation,
                                 }
                        
                        return render(request, 'admssapp/groupemidepositgetlist.html', context)
                    
                else:
                    return render(request, 'admssapp/groupemideposit.html' , context)




############################################
########## GROUP EMI DEPOSIT GET ###########
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositget(request):


         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:


                if request.method == "POST" and 'show' in request.POST:
                      
                        fgroupid = request.POST.get('groupidname')
                        floanemi = request.POST.get('emiamount')

                        epgrouploan = Loanmaster.objects.filter(locationcode=loginlocationcode,groupid = fgroupid).order_by('id')
                        epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid = fgroupid,groupleader='Y')

                        fgroupid =  epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation
 
                        Groupemicolldata.objects.filter(locationcode=loginlocationcode,groupid = fgroupid).delete()

                        for all in epgrouploan:

                            all.grouploanemi = floanemi
                            all.save()

                            gd = Groupemicolldata(locationcode = all.locationcode,
                                                  locationname = all.locationname,
                                                  groupid = all.groupid,
                                                  groupleaderloanid = all.groupleaderloanid,
                                                  groupleadername = all.groupleadername,
                                                  loanid = all.loanid,
                                                  appname = all.appname,
                                                  apploanemi = all.apploanemi,
                                                  amount=floanemi,
                                                  latefee = 0,
                                                  lastemidepdate=all.applastemidepdate,
                                                  emiduedate = all.appemiduedate,
                            #                      #delaydays = all.delaydays,
                                                  date = loginrundate,
                                                  processdate = loginrundate,
                                                  rundate = loginrundate,
                                                  status = 'N',
                                                  rpersoncode = all.rpersoncode,
                                                  rpersonname = all.rpersonname,
                                                  master_id = all.id
                                                  )
                            gd.save()
                         

                        epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')
                        summ = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid, status='N').aggregate(totac=Coalesce(
                            Count('loanid'), 0), totemi=Coalesce(Sum('apploanemi'), 0), totamt=Coalesce(Sum('amount'), 0))

                        tac = summ.get("totac")
                        temi = summ.get("totemi")
                        tamt = summ.get("totamt")



                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'tac':tac,
                                'temi':temi,
                                'tamt':tamt,
                                'epgrouploan':epgrouploan,
                                'fgroupid':fgroupid,
                                'fgroupleadername':fgroupleadername,
                                'fgrouplocation':fgrouplocation,
                                 }
                        
                        return render(request, 'admssapp/groupemidepositgetlist.html', context)


                if request.method == "POST" and 'cancel' in request.POST:
                        fgroupid = request.POST.get('groupidname')
       
                        epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

                        fgroupid =  epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation

 
                        epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'epgrouploan':epgrouploan,
                                'fgroupid':fgroupid,
                                'fgroupleadername':fgroupleadername,
                                'fgrouplocation':fgrouplocation,
                                 }
                        
                        return render(request, 'admssapp/groupemidepositgetlist.html', context)
                    
                else:
                    return render(request, 'admssapp/groupemideposit.html' , context)


############################################################
########## GROUP EMI DEPOSIT MODIFICATION CANCEL ###########
############################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositupdatecancel(request):
 

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                    
                        fgroupid = request.POST.get('groupidname')

                        epgrouploan = Loanmaster.objects.filter(locationcode=loginlocationcode,groupid=fgroupid).order_by('id')
                        epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

                        fgroupid =  epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation

                         
                        epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'epgrouploan':epgrouploan,
                                'fgroupid':fgroupid,
                                'fgroupleadername':fgroupleadername,
                                'fgrouplocation':fgrouplocation,
                                 }
                        
                        return render(request, 'admssapp/groupemidepositgetlist.html', context)



##############################################
######## GROUP EMI AMOUNT MODIFICATIONS ######
##############################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositupdate(request,emicolldata_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:
            groupcorrdata = Groupemicolldata.objects.get(id=emicolldata_id)
            fgroupid = groupcorrdata.groupid
            floanid=groupcorrdata.loanid
            fappname=groupcorrdata.master.appname
            femiduedate=groupcorrdata.master.appemiduedate
            flastemidepdate=groupcorrdata.master.applastemidepdate
            fdelaydays=groupcorrdata.delaydays
            fdate=groupcorrdata.date
            famount=groupcorrdata.amount
            flatefee=groupcorrdata.latefee
            femiamount = groupcorrdata.master.apploanemi
            fgroupleadername = groupcorrdata.master.groupleadername
            fgrouplocation = groupcorrdata.master.appshoplocation



        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'fgroupleadername':fgroupleadername,
                    'fgrouplocation':fgrouplocation,
                    'fgroupid':fgroupid,
                    'floanid':floanid,
                    'fappname':fappname,
                    'femiduedate':femiduedate,
                    'flastemidepdate':flastemidepdate,
                    'fdelaydays':fdelaydays,
                    'famount':famount,
                    'fdate':fdate,
                    'flatefee':flatefee,
                    'femiamount':femiamount,
                    'emicolldata_id':emicolldata_id,
                        }

            if groupcorrdata == None:
                pass
            else:
                return render(request,"admssapp/groupemiupdate.html", context)




#####################################################
######## GROUP EMI AMOUNT MODIFICATIONS COMMIT ######
#####################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositupdatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            fcorrid = 0
            if len(request.POST.get('myid')) >0 :
                fcorrid = int(request.POST.get('myid'))
                fgroupid = request.POST.get('groupidname')

                famount = 0
            if len(request.POST.get('famount')) > 0:
                famount =  int(request.POST.get('famount'))
            
                flatefee = 0
            if len(request.POST.get('flatefee')) > 0:
                flatefee =  (request.POST.get('flatefee'))
       
            if request.method == "POST" and 'show' in request.POST:

                groupcorrdata = Groupemicolldata.objects.get(id=fcorrid)
       
                fcollcode = groupcorrdata.rpersoncode
                fcollname = groupcorrdata.rpersonname

                groupcorrdata.amount = (famount)
                groupcorrdata.latefee = (flatefee)
                groupcorrdata.modified = 'Y'
                groupcorrdata.save()


            elif request.method == "POST" and 'cancel' in request.POST:
                pass
        
            
            epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')
            epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

            fgroupid =  epgroupleager.groupid
            fgroupleadername = epgroupleager.groupleadername
            fgrouplocation = epgroupleager.appshoplocation

            context={'loginlocationcode':loginlocationcode,
                     'loginlocationname':loginlocationname,
                     'loginrundate':loginrundate,
                     'loginstatus':loginstatus,
                     'currdate':currdate,
                     'epgrouploan':epgrouploan,
                     'fgroupid':fgroupid,
                     'fgroupleadername':fgroupleadername,
                     'fgrouplocation':fgrouplocation,
                     }
                        
            return render(request, 'admssapp/groupemidepositgetlist.html', context)
            




###############################################
######## GROUP EMI - DELETE / REMOVE   ########
###############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositdelete(request,emicolldata_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:
            groupcorrdata = Groupemicolldata.objects.get(id=emicolldata_id)
            fgroupid = groupcorrdata.groupid
            floanid=groupcorrdata.loanid
            fappname=groupcorrdata.master.appname
            femiduedate=groupcorrdata.master.appemiduedate
            flastemidepdate=groupcorrdata.master.applastemidepdate
            fdelaydays=groupcorrdata.delaydays
            fdate=groupcorrdata.date
            famount=groupcorrdata.amount
            flatefee=groupcorrdata.latefee
            femiamount = groupcorrdata.master.apploanemi
            fgroupleadername = groupcorrdata.master.groupleadername
            fgrouplocation = groupcorrdata.master.appshoplocation


        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'fgroupleadername':fgroupleadername,
                    'fgrouplocation':fgrouplocation,
                    'fgroupid':fgroupid,
                    'floanid':floanid,
                    'fappname':fappname,
                    'femiduedate':femiduedate,
                    'flastemidepdate':flastemidepdate,
                    'fdelaydays':fdelaydays,
                    'famount':famount,
                    'fdate':fdate,
                    'flatefee':flatefee,
                    'femiamount':femiamount,
                    'emicolldata_id':emicolldata_id,
                        }

            if groupcorrdata == None:
                pass
            else:
                return render(request,"admssapp/groupemidelete.html", context)




##############################################
######## GROUP EMI DELETE COMMIT  ############
##############################################
@login_required(login_url='login')
@csrf_exempt
def groupemidepositdeletecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
                fcorrid = 0
                if len(request.POST.get('myid')) >0 :
                    fcorrid = int(request.POST.get('myid'))
                    fgroupid = request.POST.get('groupidname')

                famount = 0
                if len(request.POST.get('famount')) > 0:
                    famount =  int(request.POST.get('famount'))
            
                flatefee = 0
                if len(request.POST.get('flatefee')) > 0:
                    flatefee =  (request.POST.get('flatefee'))
        
                if request.method == "POST" and 'show' in request.POST:

                    groupcorrdata = Groupemicolldata.objects.get(id=fcorrid)
       
                    fcollcode = groupcorrdata.rpersoncode
                    fcollname = groupcorrdata.rpersonname

                    groupcorrdata.amount = (famount)
                    groupcorrdata.latefee = (flatefee)
                    groupcorrdata.modified = 'Y'
                    groupcorrdata.status= 'D'
                    groupcorrdata.save()

                elif request.method == "POST" and 'cancel' in request.POST:
                    pass

                    
                epgrouploan = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').order_by('id')
                epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

                fgroupid =  epgroupleager.groupid
                fgroupleadername = epgroupleager.groupleadername
                fgrouplocation = epgroupleager.appshoplocation

                context={'loginlocationcode':loginlocationcode,
                         'loginlocationname':loginlocationname,
                         'loginrundate':loginrundate,
                         'loginstatus':loginstatus,
                         'currdate':currdate,
                         'epgrouploan':epgrouploan,
                         'fgroupid':fgroupid,
                         'fgroupleadername':fgroupleadername,
                         'fgrouplocation':fgrouplocation,
                         }
                        
                return render(request, 'admssapp/groupemidepositgetlist.html', context)






###############################################
########## GROUP EMI DEPOSIT COMMIT ###########
###############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupemidepositcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

            
                if request.method == "POST":
                    fgroupid = request.POST.get('groupidname')
                    
                    allgroupdata = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid,status='N').select_related('master').order_by('id')
                    epgroupleager = Loanmaster.objects.get(locationcode=loginlocationcode,groupid=fgroupid,groupleader='Y')

                    fgroupleadername = epgroupleager.appname
                    fgroupid = epgroupleager.groupid

                    groupsumm = Groupemicolldata.objects.filter(locationcode=loginlocationcode, groupid=fgroupid, status='N').aggregate(totac=Coalesce(Count('loanid'), 0), totamt=Coalesce(Sum('amount'), 0))

                    fgroupac = groupsumm.get("totac")
                    fgroupamt = groupsumm.get("totamt")

                    for x in allgroupdata:
                            floanid = x.loanid
                            fcashrec = x.amount
                            flatefee = x.latefee
                            fdate = x.date
                            fdelaydays = x.delaydays
                            fmode="CASH"

                            x.status="Y"
                            x.processdate=loginrundate
                            x.save()

                            eploan = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=floanid)
            
                            fmasterid = eploan.id  
                            fapploanid = eploan.loanid
                            fappname = eploan.appname
                            fapploanemi = eploan.apploanemi
                            fapploanemiprin = eploan.apploanemiprin
                            fapploanemiint = eploan.apploanemiint
                            fappemiduedate = eploan.appemiduedate
                            fapploanamt = eploan.apploanamt

                            fpersoncode = eploan.rpersoncode
                            fpersonname = eploan.rpersonname

                            flocationcode = loginlocationcode
                            flocationname = loginlocationname

                            femiprintranscd='3011'
                            femiprintransnm = 'EMI PRIN.'

                            femiinttranscd='3012'
                            femiinttransnm = 'EMI INT.'

                            flatefeetranscd='3013'
                            flatefeetransnm = 'LATE FEE.'

                    

                            if flatefee is None:
                                flatefee=0


                            fcashrecemi = int(fcashrec) - int(flatefee)

                            #### Delay Days #### 

                            delta=loginrundate-fappemiduedate
                            delaydays = (delta.days)

                            alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                            mtransidnum = alllocmast.transidnum + 1
                            mperc = alllocmast.perc
                            alllocmast.transidnum = alllocmast.transidnum + 1
                            alllocmast.save()

                    
                            ####  TRANSNUM  ####
                    
                            yy = loginrundate.strftime("%Y")
                            yy = yy[0:2]
                            mm = loginrundate.strftime("%m")
                            dd = loginrundate.strftime("%d")
                    

                            ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                            remquo = divmod(fcashrecemi,fapploanemi)
                            multi = remquo[0]
                            remain = remquo[1]
                            
  
                            
                            if multi > 0:
                                if eploan.appemifreq == "DAILY":
                                     eploan.appemiduedate = (eploan.appemiduedate + timedelta(1*multi))

                                elif eploan.appemifreq == "WEEKLY":
                                     eploan.appemiduedate = (eploan.appemiduedate + timedelta(7*multi))

                                elif eploan.appemifreq == "FORTNIGHTLY":

  
                                     eploan.appemiduedate = eploan.appemiduedate + timedelta(15*multi)
                                     if int(eploan.appemiduedate.strftime("%d")) >= 15:

                                          if eploan.appemisecondfn == '  ':
                                             eploan.appemisecondfn = '20'

                                          fappemiduedate = (eploan.appemiduedate.strftime("%Y"))+(eploan.appemiduedate.strftime("%m"))+eploan.appemisecondfn
                                          fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                                     elif int(eploan.appemiduedate.strftime("%d")) < 15:

                                          if eploan.appemifirstfn == '  ':
                                             eploan.appemifirstfn = '05'
                              
                                          fappemiduedate = (eploan.appemiduedate.strftime("%Y"))+(eploan.appemiduedate.strftime("%m"))+eploan.appemifirstfn
                                          fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                                     eploan.appemiduedate = fappemiduedate


                                elif eploan.appemifreq == "MONTHLY":
                                     eploan.appemiduedate = (eploan.appemiduedate + relativedelta(months=+1))

                            else:
                                     eploan.appemiduedate = eploan.appemiduedate
                                     fappemiduedate =  eploan.appemiduedate
                

                            
                            fcashrecemi = fcashrec - flatefee

                            fbalprinamt = eploan.apploanamt-eploan.appprinrecamt 
                            fbalintamt = eploan.apploanint-eploan.appintrecamt

                            fintamt = round(fcashrecemi*(fapploanemiint/fapploanemi))
        
                            if fbalintamt <= fintamt and fbalintamt > 0:
                                fintamt = fbalintamt
                            elif fbalintamt <= 0:
                                fintamt = 0
                
                            fprinamt = fcashrecemi - fintamt

                            if fbalprinamt <= 0:
                                fprinamt = 0 
                    
                            flatefee = flatefee + (fcashrecemi - fprinamt - fintamt)

                            if flatefee <= 0:
                                flatefee = 0

                            #finstno = eploan.instno + multi
                            #eploan.instno = eploan.instno + multi
                            eploan.applastemidepdate = loginrundate
 
                            eploan.save()
                        
                
                            fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                            fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                            fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 


                            trans = Transcd.objects.get(transcd=femiprintranscd)
                            ftrans = trans.id
                        
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            if fprinamt > 0:            
                                 db1 = Daybook(locationcode=loginlocationcode,
                                             locationname=loginlocationname,
                                             date=loginrundate,transid=ftransid,
                                             transcd=femiprintranscd,transnm=femiprintransnm,
                                             mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                             loanid=fapploanid ,appname=fappname,
                                             bankac='',
                                             narration=fnarr1,amount=fprinamt,drcr="C",
                                             trans_id = ftrans,
                                             clcashbank_id = opclid)
            
                                 db1.save()

                                 trans = Transcd.objects.get(transcd=femiinttranscd)
                                 ftrans = trans.id

                            if fintamt > 0:            
                                 db2 = Daybook(locationcode=loginlocationcode,
                                               locationname=loginlocationname,
                                               date=loginrundate,
                                               transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                               mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                               loanid=fapploanid ,appname=fappname,
                                               bankac='',
                                               narration=fnarr2,amount=fintamt,drcr="C",
                                               trans_id = ftrans,
                                               clcashbank_id = opclid)

                                 db2.save()      


                                 trans = Transcd.objects.get(transcd=flatefeetranscd)
                                 ftrans = trans.id
        
                            if flatefee > 0:
                                 db3 = Daybook(locationcode=loginlocationcode,
                                               locationname=loginlocationname,
                                               date=loginrundate,
                                               transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                               mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                               loanid=fapploanid ,appname=fappname,
                                               bankac='',
                                               narration=fnarr3,amount=flatefee,drcr="C",
                                               trans_id = ftrans,
                                               clcashbank_id = opclid)

                                 db3.save()      
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                            if fintamt > 0:
                                   fhqamt=fintamt*(mperc/100)
                                   facamt=fintamt-fhqamt
                                   for all in allcash:
                                           all.hqamt = all.hqamt + fhqamt
                                           all.acamt = all.acamt + facamt 
                                           all.save()

                          

                            if fcashrec > 0:
                                 lt = Loantrans(locationcode=flocationcode,
                                                locationname=loginlocationname,
                                                loanid=fapploanid,
                                                transid=ftransid,duedate=fappemiduedate,
                                                date=loginrundate,delaydays=(delta.days),
                                                amount=fcashrec-flatefee,prinamt=fprinamt,
                                                intamt=fintamt,latefee=flatefee,mode=fmode,
                                                drcr="C",master_id=fmasterid)
                                    
                                 lt.save()

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                            for all in allcash:
                                    all.clcash = all.clcash + int(fcashrec)
                                    all.save()

                            eploan.apptotalrecamt = eploan.apptotalrecamt + (fcashrec-flatefee) 
                            eploan.appprinrecamt = eploan.appprinrecamt + fprinamt
                            eploan.appintrecamt = eploan.appintrecamt + fintamt
                            eploan.applatefeeamt = eploan.applatefeeamt + flatefee
                            eploan.groupemicoll = 'N'

                            eploan.save()

                    
                    success=True
                    message = "Group EMI " + fgroupleadername + " Total a/c - " +  str(fgroupac) + " Rs. - " + str(fgroupamt) + " Processed Succesfully."
                    messages.success(request, message)
                    return redirect('/groupemideposit/')


########## COLL EMI ##############
##################################
########## EMI DEPOSIT ###########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemidepositbranch(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
            

                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').order_by('id')
            
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0))
            


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        'collsumm':collsumm,
                        }

                
            
                if request.method == "POST":
                    fcollcode = request.POST.get('collcode')
                    allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).order_by('id').select_related('master')
                    collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')


                    context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'collsumm':collsumm,
                        'allcolldata':allcolldata,
                        }
        
                    return render(request, 'admssapp/collemiprocessbranch.html' , context)
            
                else:
                    return render(request, 'admssapp/collemidepositbranch.html' , context)



########## COLL EMI ##############
##################################
########## EMI PROCESS ###########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemiprocessbranch(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').order_by('id')
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0))

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'collsumm':collsumm,
                         }

            
                if request.method == "POST":
                    fcollcode = request.POST.get('collcode')
                    allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).order_by('id').select_related('master').order_by('id')
                    collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')


                    context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'collsumm':collsumm,
                        'allcolldata':allcolldata,
                        }
                    return render(request, 'admssapp/collemiprocessbranch.html' , context)
            
                else:
                    return render(request, 'admssapp/collemidepositbranch.html' , context)




########## COLL EMI  COMMIT ######
##################################
############ EMI COMMIT ##########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemifinalbranch(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').order_by('id')
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0))
            

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginstatus':loginstatus,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        }

            
                if request.method == "POST":
                    fcollcode = request.POST.get('collcode')
                    
                    collname = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode)
                
                    if len(collname) > 0:
                        fcollname = collname[0].rpersonname
                    
                    colla = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).aggregate(totac=Coalesce(Count('loanid'),0))
                    collt = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).aggregate(totamt=Coalesce(Sum('amount'),0))

                    fcollac = colla.get("totac")
                    fcollamt = collt.get("totamt")


                    allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).select_related('master')
                    collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')


                    for x in allcolldata:
                            floanid = x.loanid
                            fcashrec = x.amount
                            flatefee = x.latefee
                            fdate = x.date
                            fdelaydays = x.delaydays
                            fmode="CASH"

                            x.status="Y"
                            x.processdate=loginrundate
                            x.save()


                            eploan = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=floanid)
            
                            fmasterid = eploan.id  
                            fapploanid = eploan.loanid
                            fappname = eploan.appname
                            fapploanemi = eploan.apploanemi
                            fapploanemiprin = eploan.apploanemiprin
                            fapploanemiint = eploan.apploanemiint
                            fappemiduedate = eploan.appemiduedate
                            fapploanamt = eploan.apploanamt

                            fpersoncode = eploan.rpersoncode
                            fpersonname = eploan.rpersonname

                            flocationcode = loginlocationcode
                            flocationname = loginlocationname

                            fapploanemi,fapploanemiprin,fapploanemiint,fapploanint = updateamount(fapploanid, loginlocationcode, loginrundate)



                            femiprintranscd='3011'
                            femiprintransnm = 'EMI PRIN.'

                            femiinttranscd='3012'
                            femiinttransnm = 'EMI INT.'

                            flatefeetranscd='3013'
                            flatefeetransnm = 'LATE FEE.'

                    

                            if flatefee is None:
                                flatefee=0


                            fcashrecemi = int(fcashrec) - int(flatefee)

                            #### Delay Days #### 

                            delta=loginrundate-fappemiduedate
                            delaydays = (delta.days)

                            alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                            mtransidnum = alllocmast.transidnum + 1
                            mperc = alllocmast.perc
                            alllocmast.transidnum = alllocmast.transidnum + 1
                            alllocmast.save()

                    
                            ####  TRANSNUM  ####
                    
                            yy = loginrundate.strftime("%Y")
                            yy = yy[0:2]
                            mm = loginrundate.strftime("%m")
                            dd = loginrundate.strftime("%d")
                    

                            ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                            remquo = divmod(fcashrecemi,fapploanemi)
                            multi = remquo[0]
                            remain = remquo[1]

                            if multi > 0:
                                   if eploan.appemifreq == "DAILY":
                                       eploan.appemiduedate = (eploan.appemiduedate + timedelta(1*multi))
                                       fappemiduedate = (eploan.appemiduedate + timedelta(1*multi))

                                   elif eploan.appemifreq == "WEEKLY":
                                       eploan.appemiduedate = (eploan.appemiduedate + timedelta(7*multi))
                                       fappemiduedate = (eploan.appemiduedate + timedelta(7*multi))

                                   elif eploan.appemifreq == "FORTNIGHTLY":

                                       eploan.appemiduedate = eploan.appemiduedate + timedelta(15*multi)
                                       if int(eploan.appemiduedate.strftime("%d")) >= 15:

                                            if eploan.appemisecondfn == '  ':
                                               eploan.appemisecondfn = '20'

                                            fappemiduedate = (eploan.appemiduedate.strftime("%Y"))+(eploan.appemiduedate.strftime("%m"))+eploan.appemisecondfn
                                            fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                                     
                                       elif int(eploan.appemiduedate.strftime("%d")) < 15:

                                            if eploan.appemifirstfn == '  ':
                                               eploan.appemifirstfn = '05'
                              
                                            fappemiduedate = (eploan.appemiduedate.strftime("%Y"))+(eploan.appemiduedate.strftime("%m"))+eploan.appemifirstfn
                                            fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                                    
                                       eploan.appemiduedate = fappemiduedate



                                   elif eploan.appemifreq == "MONTHLY":
                                       eploan.appemiduedate = (eploan.appemiduedate + relativedelta(months=+1))
                                       fappemiduedate = (eploan.appemiduedate + relativedelta(months=+1))


                            else:
                                eploan.appemiduedate = eploan.appemiduedate
                        


                            fbalprinamt = eploan.apploanamt - eploan.appprinrecamt 
                            fbalintamt = fapploanint - eploan.appintrecamt

                            ##########################
                            fintamt = round(fcashrecemi*(fapploanemiint/fapploanemi))
                            fintamt = round(fintamt*.95)
                            ##########################

                            if (eploan.appprinrecamt+eploan.appintrecamt) >= (eploan.apploanamt+eploan.apploanint) :
                                fbalintamt = 0
        
                            if fbalintamt <= fintamt and fbalintamt > 0:
                                fintamt = fbalintamt
                            elif fbalintamt <= 0:
                                fintamt = 0
                
                            fprinamt = fcashrecemi - fintamt

                            if fbalprinamt <= 0:
                                fprinamt = 0 
                    
                            flatefee = flatefee + (fcashrecemi - fprinamt - fintamt)

                            if flatefee <= 0:
                                flatefee = 0


                            #finstno = eploan.instno + multi
                            #eploan.instno = eploan.instno + multi
                            eploan.applastemidepdate = loginrundate

                            eploan.save()
                        
                
                            fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                            fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                            fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 


                            trans = Transcd.objects.get(transcd=femiprintranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                        
                            if fprinamt > 0:            
                                db1 = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=femiprintranscd,transnm=femiprintransnm,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    loanid=fapploanid ,appname=fappname,
                                    bankac='',
                                    narration=fnarr1,amount=fprinamt,drcr="C",
                                    trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db1.save()

                            trans = Transcd.objects.get(transcd=femiinttranscd)
                            ftrans = trans.id

                            if fintamt > 0:            
                                db2 = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,
                                    transid=ftransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    loanid=fapploanid ,appname=fappname,
                                    bankac='',
                                    narration=fnarr2,amount=fintamt,drcr="C",
                                    trans_id = ftrans,
                                    clcashbank_id = opclid)

                                db2.save()      


                            trans = Transcd.objects.get(transcd=flatefeetranscd)
                            ftrans = trans.id
        
                            if flatefee > 0:
                                db3 = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,
                                    transid=ftransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    loanid=fapploanid ,appname=fappname,
                                    bankac='',
                                    narration=fnarr3,amount=flatefee,drcr="C",
                                    trans_id = ftrans,
                                    clcashbank_id = opclid)

                                db3.save()      
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                            if fintamt > 0:
                                fhqamt=fintamt*(mperc/100)
                                facamt=fintamt-fhqamt
                                for all in allcash:
                                        all.hqamt = all.hqamt + fhqamt
                                        all.acamt = all.acamt + facamt 
                                        all.save()


                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        


                            if fcashrec > 0:
                                lt = Loantrans(locationcode=flocationcode,
                                    locationname=loginlocationname,
                                    loanid=fapploanid,
                                    transid=ftransid,duedate=fappemiduedate,
                                    date=loginrundate,delaydays=(delta.days),
                                    amount=fcashrec-flatefee,prinamt=fprinamt,
                                    intamt=fintamt,latefee=flatefee,mode=fmode,
                                    drcr="C",master_id=fmasterid)
                                    
                                lt.save()

                            for all in allcash:
                                    all.clcash = all.clcash + int(fcashrec)
                                    all.save()


                            eploan.apptotalrecamt = eploan.apptotalrecamt + (fcashrec-flatefee) 
                            eploan.appprinrecamt = eploan.appprinrecamt + fprinamt
                            eploan.appintrecamt = eploan.appintrecamt + fintamt
                            eploan.applatefeeamt = eploan.applatefeeamt + flatefee
                            eploan.groupemicoll = 'N'
                            eploan.save()


                            collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
                
                    
                    success=True
                    message = "EMI Collected by " + fcollname + " Total a/c " + str(fcollac) + " Rs. " + str(fcollamt) + " Processed Succesfully."

                    messages.success(request, message)
                    return redirect('/collemidepositbranch/')
    
    


##############################################
######## COLL EMI  AMOUNT MODIFICATIONS ######
##############################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemidepositupdate(request,emicolldata_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:

            collcorrdata=Emicolldata.objects.get(id=emicolldata_id)
            floanid=collcorrdata.loanid
            fappname=collcorrdata.master.appname
            femiduedate=collcorrdata.master.appemiduedate
            flastemidepdate=collcorrdata.master.applastemidepdate
            fdelaydays=collcorrdata.delaydays
            fdate=collcorrdata.date
            famount=collcorrdata.amount
            flatefee=collcorrdata.latefee
            femiamount=collcorrdata.master.apploanemi

        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'floanid':floanid,
                    'fappname':fappname,
                    'femiduedate':femiduedate,
                    'flastemidepdate':flastemidepdate,
                    'fdelaydays':fdelaydays,
                    'famount':famount,
                    'fdate':fdate,
                    'flatefee':flatefee,
                    'femiamount':femiamount,
                    'emicolldata_id':emicolldata_id,
                        }


            if collcorrdata==None:
                pass
            else:
                return render(request,"admssapp/collemiupdate.html", context)




##############################################
######## COLL EMI LATE AMOUNT/LATE FEE  ######
##############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemidepositupdatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                fcollid = 0
                if len(request.POST.get('myid')) >0 :
                    fcollid = int(request.POST.get('myid'))

                famount = 0
                if len(request.POST.get('famount')) > 0:
                    famount =  int(request.POST.get('famount'))
            
                flatefee = 0
                if len(request.POST.get('flatefee')) > 0:
                    flatefee =  (request.POST.get('flatefee'))
        
                collcorrdata=Emicolldata.objects.get(id=fcollid)

                fcollcode = collcorrdata.rpersoncode
                fcollname = collcorrdata.rpersonname

                collcorrdata.amount = (famount)
                collcorrdata.latefee = (flatefee)
                collcorrdata.modified = 'Y'
                collcorrdata.save()

                    
                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).select_related('master').order_by('rpersoncode','id')
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'collsumm':collsumm,
                        'allcolldata':allcolldata,
                        }

                return render(request, 'admssapp/collemiprocessbranch.html' , context)
            




##############################################
######## COLL EMI - DELETE / REMOVE   ########
##############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemidepositdelete(request,emicolldata_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:

            collcorrdata=Emicolldata.objects.get(id=emicolldata_id)
            floanid=collcorrdata.loanid
            fappname=collcorrdata.master.appname
            femiduedate=collcorrdata.master.appemiduedate
            flastemidepdate=collcorrdata.master.applastemidepdate
            fdelaydays=collcorrdata.delaydays
            fdate=collcorrdata.date
            famount=collcorrdata.amount
            flatefee=collcorrdata.latefee
            femiamount=collcorrdata.master.apploanemi

        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'floanid':floanid,
                    'fappname':fappname,
                    'femiduedate':femiduedate,
                    'flastemidepdate':flastemidepdate,
                    'fdelaydays':fdelaydays,
                    'famount':famount,
                    'fdate':fdate,
                    'flatefee':flatefee,
                    'femiamount':femiamount,
                    'emicolldata_id':emicolldata_id,
                        }


            if collcorrdata==None:
                pass
            else:
                return render(request,"admssapp/collemidelete.html", context)




##############################################
######## COLL EMI DELETE FINAL  ##############
##############################################
@login_required(login_url='login')
@csrf_exempt
def collemidepositdeletecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()

    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
         return HttpResponseRedirect('/login')
    else:

            if request.method == "POST":
                fcollid = int(request.POST.get('myid'))
                famount =  request.POST.get('amount')
                flatefee =  request.POST.get('latefee')

                collcorrdata=Emicolldata.objects.get(id=fcollid)

                fcollcode = collcorrdata.rpersoncode
                fcollname = collcorrdata.rpersonname

                collcorrdata.modified = 'Y'
                collcorrdata.status= 'D'

                collcorrdata.save()
                    
                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).select_related('master').order_by('rpersoncode','id')
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N',rpersoncode=fcollcode).values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'collsumm':collsumm,
                        'allcolldata':allcolldata,
                        }
                return render(request, 'admssapp/collemiprocessbranch.html' , context)




##################################
####### SUNDRY EMI DEPOSIT #######
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emisundry(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')

                transdate = loginrundate.strftime("%Y-%m-%d")

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'success':False,
                        'transdate':transdate,
                        }

                
            
                if request.method == "POST":

                        fcashrec=0
                    
                        if len(request.POST.get('cashrec'))>0:
                            fcashrec = int(request.POST.get('cashrec'))

                        fmode = request.POST.get('emimode').upper()
                        fappbankac = request.POST.get('appbankac')
                        fappbankchq = request.POST.get('appbankchq')
                        fremark = request.POST.get('remark')
                        ftransdate = request.POST.get('transdate')
                    
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        mperc = alllocmast.perc
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()
                    
                        ####  TRANSNUM  ####
                    
                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")

                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)    

                        femisundrytranscd='3381'
                        femisundrytransnm = 'EMI SUNDRY'

                        trans = Transcd.objects.get(transcd=femisundrytranscd)
                        ftrans = trans.id

                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                        opclid = allcash.id

                        fnarr="EMI SUNDRY"    
       

                        if fcashrec > 0:            
                            db1 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=femisundrytranscd,transnm=femisundrytransnm,
                                mode=fmode,
                                bankac=fappbankac,
                                narration=fnarr,
                                amount=fcashrec,
                                drcr="C",
                                remark=fremark,
                                trans_id=ftrans,
                                clcashbank_id=opclid)
            
                            db1.save()
                        
     
                        if fmode == "CASH":
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash + fcashrec
                                all.save()


                        if fmode == "BANK":

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            opclid = allbank.id

                            trans = Transcd.objects.get(transcd=allbank.bankcode)
                            ftrans = trans.id


                            db = Daybook(locationcode = loginlocationcode,
                                    locationname=loginlocationname,
                                    transid = ftransid,
                                    amount = int(fcashrec),
                                    date = loginrundate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid)
                
                            db.save()             
        
                    
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + fcashrec
                            allbank.save()


                        sundry = Emisundry(locationcode = loginlocationcode,
                                           locationname=loginlocationname,
                                           transid = ftransid,
                                           amount = int(fcashrec),
                                           date = loginrundate,
                                           mode=fmode,
                                           transdate = ftransdate,
                                           status = 'A')
                        sundry.save()

                        message = "EMI SUNDRY "+"Rs."+str(fcashrec)+" / Processed Succesfully through "+fmode

                        messages.success(request, message)
                        return HttpResponseRedirect('/emisundry/')

                    
                else:
                    return render(request, 'admssapp/emisundry.html' , context)




##########################################
####### PROCESS SUNDRY EMI DEPOSIT #######
##########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emisundryprocess(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                allsundry = Emisundry.objects.filter(locationcode=loginlocationcode,status='A').order_by('id')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allsundry':allsundry,
                        }

            
                if request.method == "POST":
                    pass
                else:
                    return render(request, 'admssapp/emisunderyprocess.html' , context)




##################################################
######## PROCESS SUNDRY EMI DEPOSIT GET   ########
##################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emisundryprocessget(request,sundry_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:

            sundrydata=Emisundry.objects.get(id=sundry_id)
            famount=sundrydata.amount
            fmode=sundrydata.mode
            fdate=sundrydata.date.strftime("%Y-%m-%d")
            ftransdate=sundrydata.transdate.strftime("%Y-%m-%d")

            nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
            allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
            
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'sundrydata':sundrydata,
                    'famount':famount,
                    'fmode':fmode,
                    'fdate':fdate,
                    'ftransdate':ftransdate,
                    'sundry_id':sundry_id,
                    'nname':nname,
                    'allbank':allbank,
                        }

            if sundrydata==None:
                pass
            else:
                return render(request,"admssapp/emisunderyprocessget.html", context)



###################################
########### EMI COMMIT ############
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emisundryprocesscommit(request):
     
    #if request.user.is_authenticated:
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
              return HttpResponseRedirect('/login')
         else:
   
            
                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec=0
                    flatefee=0
                    
                    if len(request.POST.get('cashrec'))>0:
                        fcashrec = int(request.POST.get('cashrec'))

                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fsundryid = request.POST.get('sundryid')

                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)

                    sundrydata=Emisundry.objects.get(id=fsundryid)
                    sundrydate = sundrydata.transdate
                    fsundrytransid = sundrydata.transid
            
                    floanid = loanmast.id
                    fapploanid = loanmast.loanid
                    fappname = loanmast.appname
                    fapploanemi = loanmast.apploanemi
                    fapploanemiprin = loanmast.apploanemiprin
                    fapploanemiint = loanmast.apploanemiint
                    fappemiduedate = loanmast.appemiduedate
                    fapploanamt = loanmast.apploanamt
                    fmasterid = loanmast.id

                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname


                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    femiprintranscd='3011'
                    femiprintransnm = 'EMI PRIN.'

                    femiinttranscd='3012'
                    femiinttransnm = 'EMI INT.'

                    flatefeetranscd='3013'
                    flatefeetransnm = 'LATE FEE.'


                    fcashrecemi = fcashrec - flatefee


                    remquo = divmod(fcashrecemi,fapploanemi)
                    multi = remquo[0]
                    remain = remquo[1]

    
                    if multi > 0:
                        if loanmast.appemifreq == "DAILY":
                            loanmast.appemiduedate = (loanmast.appemiduedate + timedelta(1*multi))


                        elif loanmast.appemifreq == "WEEKLY":
                            loanmast.appemiduedate = (loanmast.appemiduedate + timedelta(7*multi))


                        elif loanmast.appemifreq == "FORTNIGHTLY":

                            loanmast.appemiduedate = loanmast.appemiduedate + timedelta(15*multi)
                            if int(loanmast.appemiduedate.strftime("%d")) >= 15:

                                   if loanmast.appemisecondfn == '  ':
                                       loanmast.appemisecondfn = '20'

                                   fappemiduedate = (loanmast.appemiduedate.strftime("%Y"))+(loanmast.appemiduedate.strftime("%m"))+loanmast.appemisecondfn
                                   fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                     
                            elif int(loanmast.appemiduedate.strftime("%d")) < 15:

                                    if loanmast.appemifirstfn == '  ':
                                       loanmast.appemifirstfn = '05'
                              
                                    fappemiduedate = (loanmast.appemiduedate.strftime("%Y"))+(loanmast.appemiduedate.strftime("%m")) + loanmast.appemifirstfn
                                    fappemiduedate = datetime.strptime(fappemiduedate, '%Y%m%d')
                            
                            loanmast.appemiduedate = fappemiduedate


                        elif loanmast.appemifreq == "MONTHLY":
                            fappemiduedate = (loanmast.appemiduedate + relativedelta(months=+1))


                    else:
                        loanmast.appemiduedate = loanmast.appemiduedate
                        fappemiduedate =  loanmast.appemiduedate


                    fcolldaychar = loanmast.appemiduedate.strftime('%A')
                    fcolldaynum = loanmast.appemiduedate.strftime('%w')


                    fcashrecemi = fcashrec - flatefee

                    fbalprinamt = loanmast.apploanamt-loanmast.appprinrecamt 
                    fbalintamt = loanmast.apploanint-loanmast.appintrecamt

                    fintamt = round(fcashrecemi*(fapploanemiint/fapploanemi))
        
                    if fbalintamt <= fintamt and fbalintamt > 0:
                        fintamt = fbalintamt
                    elif fbalintamt <= 0:
                        fintamt = 0
                
                    fprinamt = fcashrecemi - fintamt

                    if fbalprinamt <= 0:
                        fprinamt = 0 
                    
                    flatefee = flatefee + (fcashrecemi - fprinamt - fintamt)

                    if flatefee <= 0:
                        flatefee = 0

                    #finstno = loanmast.instno + multi
                    #loanmast.instno = loanmast.instno + multi
                    loanmast.applastemidepdate = loginrundate
                    loanmast.colldaychar = fcolldaychar
                    loanmast.colldaynum = fcolldaynum
                    loanmast.groupemicoll = 'N'
                    loanmast.save()

                
                    fnarr1 = femiprintransnm+"/"+fappname.strip()+"/"+fapploanid
                    fnarr2 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 
                    fnarr3 = femiinttransnm+"/"+fappname.strip()+"/"+fapploanid 



                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    mperc = alllocmast.perc
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()
                    
                        ####  TRANSNUM  ####
                    
                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)    


                    trans = Transcd.objects.get(transcd=femiprintranscd)
                    ftrans = trans.id

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                    opclid = allcash.id

                    if fprinamt > 0:            
                        db1 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=sundrydate,transid=fsundrytransid,
                                transcd=femiprintranscd,transnm=femiprintransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr1,amount=fprinamt,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid
                                )
            
                        db1.save()


                    trans = Transcd.objects.get(transcd=femiinttranscd)
                    ftrans = trans.id

                    if fintamt > 0:            
                        db2 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=sundrydate,
                                transid=fsundrytransid,transcd=femiinttranscd,transnm=femiinttransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr2,amount=fintamt,drcr="C",
                                trans_id=ftrans,
                                clcashbank_id = opclid
                                )

                        db2.save()      

        
                    trans = Transcd.objects.get(transcd=flatefeetranscd)
                    ftrans = trans.id

                    if flatefee > 0:
                        db3 = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=sundrydate,
                                transid=fsundrytransid,transcd=flatefeetranscd,transnm=flatefeetransnm,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                loanid=fapploanid ,appname=fappname,
                                bankac=fappbankac,
                                narration=fnarr3,amount=flatefee,drcr="C",
                                trans_id = ftrans,
                                clcashbank_id = opclid)

                        db3.save()      
            
                    if fintamt > 0:
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mperc = alllocmast.perc

                        fhqamt=fintamt*(mperc/100)
                        facamt=fintamt-fhqamt
                        for all in allcash:

                                #all.hqamt = all.hqamt + round(fintamt*(mperc/100))
                                all.hqamt = all.hqamt + fhqamt
                                all.acamt = all.acamt + facamt 

                                all.save()


                    if fmode == "CASH":
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        #for all in allcash:
                        #    all.clcash = all.clcash + fcashrec
                        #    all.save()


                    if fmode == "BANK":

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        opclid = allbank.id


                        trans = Transcd.objects.get(transcd=allbank.bankcode)
                        ftrans = trans.id

 
                        fnarr="EMI DEPOSIT/"+fappname.strip()+"/"+fapploanid
                        db = Daybook(locationcode = flocationcode,
                                    locationname=loginlocationname,
                                    loanid = fapploanid,
                                    transid = ftransid,
                                    appname = fappname,
                                    amount = int(fcashrec),
                                    date = sundrydate,
                                    transcd = allbank.bankcode,
                                    transnm = allbank.bankname, 
                                    bankac = allbank.bankac,
                                    chequeno = fappbankchq,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    narration = fnarr,
                                    mode = fmode,
                                    drcr = 'D',
                                    trans_id = ftrans,
                                    clcashbank_id = opclid
                                    )
                        db.save()    


                        femisundrytranscd='3381'
                        femisundrytransnm = 'EMI SUNDRY'

                        trans = Transcd.objects.get(transcd=femisundrytranscd)
                        ftrans = trans.id

                        fnarr="EMI SUNDRY"   
                        fremark='SUNDRY CLEARANCE'


                        sundry = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=femisundrytranscd,transnm=femisundrytransnm,
                                mode=fmode,
                                bankac=fappbankac,
                                narration=fnarr,
                                amount=int(fcashrec),
                                drcr="D",
                                remark=fremark,
                                trans_id=ftrans,
                                clcashbank_id=opclid)
            
                        sundry.save()         
        

                    if fcashrec > 0:
                            lt = Loantrans(locationcode=flocationcode,
                                        locationname=loginlocationname,
                                        loanid=fapploanid,
                                        transid=fsundrytransid,duedate=fappemiduedate,
                                        date=sundrydate,delaydays=0,
                                        amount=fcashrec-flatefee,prinamt=fprinamt,
                                        intamt=fintamt,latefee=flatefee,mode=fmode,
                                        drcr="C",master_id=fmasterid)
                                    
                            lt.save()

                    loanmast.apptotalrecamt = loanmast.apptotalrecamt + (fcashrec-flatefee)
                    loanmast.appprinrecamt = loanmast.appprinrecamt + fprinamt
                    loanmast.appintrecamt = loanmast.appintrecamt + fintamt
                    loanmast.applatefeeamt = loanmast.applatefeeamt + flatefee
                    loanmast.save()

                    sundrydata=Emisundry.objects.get(id=fsundryid)
                    sundrydata.loanid = fapploanid
                    sundrydata.appname = fappname
                    sundrydata.apploanemi = fapploanemi
                    sundrydata.processdate = loginrundate
                    sundrydata.processtransid = ftransid
                    sundrydata.status = 'C'
                    sundrydata.save()

                    message = "SUNDRY EMI of "+fappname+" / "+fapploanid+" / "+"Rs."+str(fcashrec)+" / Processed Succesfully..."

                    messages.success(request, message)
                    return HttpResponseRedirect('/emisundryprocess/')



###########################################
########## EMI RECEIPT PRINTING ###########
###########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emireceipt(request):
     


         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:

                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(
                    locationcode=loginlocationcode, status='A').order_by('loanid', 'apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        'success':False,
                        }
            
                if request.method == "POST":
                    
                        floaniddate = request.POST.get('loaniddate')
  
                        if floaniddate == "LOANID":
                            loanid = Loanmaster.objects.filter(status='A').order_by('appname','apploandate')
                 
                            context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'loanid': loanid,
                                'floaniddate': floaniddate,
                                }
                        
                            return render(request, 'admssapp/emireceiptloanid.html' , context)

                        if floaniddate == "DATE":
                            dateid = Loantrans.objects.all().order_by('-date').distinct('date')
                 
                            context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'dateid': dateid,
                                'floaniddate': floaniddate,
                                }
                        
                            return render(request, 'admssapp/emireceiptdateid.html' , context)

                else:
                    return render(request, 'admssapp/emireceipt.html', context)




##################################################
########## LOANID EMI RECEIPT PRINTING ###########
##################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emireceiptloanid(request):
     


         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:
            
                if request.method == "POST":
                        floanid = request.POST.get('loanid')
                        floaniddate = request.POST.get('loaniddate')

                        loantrans = Loantrans.objects.filter(loanid=floanid).order_by('date')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate': currdate,
                                'floaniddate': floaniddate,
                                'floanid': floanid,
                                'loantrans': loantrans,
                                }
                        
                        return render(request, 'admssapp/emireceiptloanidget.html' , context)



##################################################
########## TRANSID EMI RECEIPT PRINTING ##########
##################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emireceiptloanidget(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
               return HttpResponseRedirect('/login')
         else:



            
                if request.method == "POST":
                        floanid = request.POST.get('loanid')
                        floaniddate = request.POST.get('loaniddate')
                        ftransid =  request.POST.get('transid')

                        loantrans = Loantrans.objects.filter(loanid=floanid).order_by('date')
                        transid = Loantrans.objects.get(transid=ftransid)
                        loanmaster = Loanmaster.objects.get(loanid=transid.loanid)
                        
                        receiptno = transid.transid
                        transdate = transid.date
                        famount = transid.amount + transid.latefee
                        amount = ('%.2f' % famount)
                        flocationname = loginlocationname
                        appname = loanmaster.appname
                        mode = transid.mode
                        inwords = num2words(amount)
                        loanid = loanmaster.loanid
                        

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'floaniddate': floaniddate,
                                'floanid': floanid,
                                'loantrans': loantrans,
                                'loanmaster': loanmaster,
                                'transid': transid,
                                'receiptno': receiptno,
                                'transdate': transdate,
                                'amount': amount,
                                'flocationname': flocationname,
                                'appname': appname,
                                'mode': mode,
                                'loanid': loanid,
                                'inwords': inwords,
                                }
                        
                        return render(request, 'admssapp/emireceiptloanidprint.html' , context)



########################
#### EMI DUE REPORT ####
########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def emiduereport(request):
     
 
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         fduedate = loginrundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

        
                emicoll = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'fduedate':fduedate,
                        'emicoll': emicoll,
                        }
            
                if request.method == "POST":

                    fduedate = request.POST.get('duedate')
                    femicoll = request.POST.get('recovofficer')

           
                    ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                    ftodate = ffromdate + timedelta(days=5)
                
                    #xfromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()
                
                    fduedate =  datetime.strptime(fduedate, "%Y-%m-%d").date()

                    allr = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A")

                    for all in allr:

                        if all.applastemidepdate is not None:
                           if all.appemiduedate <= loginrundate:
                              if all.applastemidepdate >= ffromdate:
                                 all.delaydays1 = 1

                              elif (loginrundate - all.applastemidepdate).days >= 14:
                                 all.delaydays1 = 2    
                           else:
                                 all.delaydays1 = 0    

                              #last_14_days = loginrundate - timedelta(days=14)

                        all.save()


                    if femicoll=='' or femicoll=='ALL':
                        femicoll=''
                        fpersoncode=''
                        fpersonname='All LoanID'
                        #allr = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A", delaydays1__in=[1, 2]).order_by('colldaynum')
                        #balsumm = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(appemiduedate__lte=ftodate)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))
                        bal = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(
                            appemiduedate__lte=loginrundate)).values('colldaychar', 'colldaynum').annotate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0)).order_by('colldaynum')

                        balsumm = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(
                            appemiduedate__lte=loginrundate)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

                        allr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(
                            locationcode=loginlocationcode) & Q(status='A') & Q(appemiduedate__lte=loginrundate)).order_by('colldaynum', 'id')
                    else:
                        person = Personmaster.objects.get(personcode=femicoll)

                        fpersoncode=person.personcode
                        fpersonname=person.personname
                        #allr = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A", rpersoncode=fpersoncode, delaydays1__in=[
                        #                                 1, 2]).order_by('colldaynum')
                        allr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(
                            locationcode=loginlocationcode) & Q(status='A') & Q(appemiduedate__lte=loginrundate), rpersoncode=fpersoncode).order_by('colldaynum', 'id')
            
                        bal = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(
                            appemiduedate__lte=loginrundate, rpersoncode=fpersoncode)).values('colldaychar', 'colldaynum').annotate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0)).order_by('colldaynum')

                        balsumm = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(
                            appemiduedate__lte=loginrundate, rpersoncode=fpersoncode)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

                    totac = balsumm.get("totac")
                    totamt = balsumm.get("totloan")
                    totemi = balsumm.get("totemi")

                    context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'currdate':currdate,
                             'loginstatus':loginstatus,
                             'fduedate':fduedate,
                             'fpersonname':fpersonname,
                             'fpersoncode':fpersoncode,
                             'allr': allr,
                             'bal':bal,
                             'totac':totac,
                             'totemi':totemi
                              }
        
                    return render(request, 'admssapp/emiduereportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/emiduereport.html' , context)





##################################
#### DASHBOARD EMI DUE REPORT ####
##################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardemiduereport(request):
     
 
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                 return HttpResponseRedirect('/login')
             else:


                    emidue =  Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',instoverdue__gte=2).order_by("-instoverdue")
                    emiduesumm =  Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',instoverdue__gte=2).aggregate(totac=Count("loanid"), totdueamt=Sum("instoverdueamt"),)

                    fdate = ll.rundate

                    last_14_days = loginrundate - timedelta(days=14)
                    last_37_days = loginrundate - timedelta(days=37)
                    last_7_days = loginrundate - timedelta(days=7)
                    last_28_days = loginrundate - timedelta(days=28)
                
                    ffromdate = last_14_days
                    ftodate = ll.rundate

                    summallr = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_14_days, appemiduedate__lt=last_14_days, status="A").aggregate(totac=Count("loanid"), totemi=Sum("apploanemi"), totbalamt=Sum("apploanbalamt"),)

                    #iramt = Loanmaster.objects.filter(locationcode=loginlocationcode,applastemidepdate__lte=last_14_days,status="A").aggregate(total = Sum("apploanemi"))
                    allrweekly = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_14_days,appemiduedate__lt=last_14_days,appemifreq='WEEKLY', status="A").order_by('applastemidepdate')

                    allrmonthly = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_37_days,appemiduedate__lt=last_37_days,appemifreq='MONTHLY', status="A").order_by('applastemidepdate')

                    allrdaily = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_7_days,appemiduedate__lt=last_7_days,appemifreq='DAILY' ,status="A").order_by('applastemidepdate')

                    allrfortnightly = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_28_days,appemiduedate__lt=last_28_days,appemifreq='FORTNIGHTLY', status="A").order_by('applastemidepdate')

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'fdate':fdate,
                            'allrweekly': allrweekly,
                            'allrmonthly':allrmonthly,
                            'allrdaily':allrdaily,
                            'allrfortnightly':allrfortnightly,
                            'summallr':summallr,
                            'emidue':emidue,
                            'emiduesumm':emiduesumm,
                            }
        
                    return render(request, 'admssapp/emiirregulareportshow.html' , context)
            
  

############################
#### EMI DEPOSIT REPORT ####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emidepositreport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

  
  
        
                ffromdate = ll.rundate
                ftodate = ll.rundate
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        }

            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          
        
                    
                    emidepac = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    emidepamt = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('amount'),0))
                    emilf = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('latefee'),0))
                    
                    allr = Loantrans.objects.filter(date__range=(
                        ffromdate, ftodate), locationcode=loginlocationcode).select_related('master')
                    for all in allr:
                        if all.amount >= all.master.apploanemi:
                            all.flag="Y"
                        else:
                            all.flag="N"
                        all.save()

            

                    allr = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).order_by('date','id')
                

                    emiac = emidepac.get("total")
                    emiamt = emidepamt.get("total")
                    emilatefee = emilf.get("total")
                    emiamt = emiamt + emilatefee

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'emiac':emiac,
                            'emiamt':emiamt,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'allr': allr,
                            }
                    
       
                    return render(request, 'admssapp/emidepositreportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/emidepositreport.html' , context)


######################################
#### DASHBOARD EMI DEPOSIT REPORT ####
######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardemidepositreport(request):
     
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                 return HttpResponseRedirect('/login')
             else:

                    
                    ffromdate = ll.rundate
                    ftodate = ll.rundate
        

                    ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                    ftodate = ffromdate + timedelta(days=5)

                    dueac = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & (Q(appemiduedate__lte=ftodate) | Q(applastemidepdate__gte=ffromdate))).values('locationcode','locationname').aggregate(totalac=Coalesce(Count('loanid'),0),totalloan=Coalesce(Sum('apploanamt'), 0),totalemi=Coalesce(Sum('apploanemi'), 0))
                    totalac = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A')).values('locationcode','locationname').aggregate(totalac=Coalesce(Count('loanid'),0),totalloan=Coalesce(Sum('apploanamt'), 0),totalemi=Coalesce(Sum('apploanemi'), 0))

                    dac = dueac.get("totalac")
                    damt = dueac.get("totalloan")
                    demi = dueac.get("totalemi")

                    tac = totalac.get("totalac")
                    tamt = totalac.get("totalloan")
                    temi = totalac.get("totalemi")

                    settletotal = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status='C').aggregate(totac=Coalesce(Count('loanid'),0),totloan=Coalesce(Sum('apploanamt'),0),totemi=Coalesce(Sum('apploanemi'),0))
    
                    sac = settletotal.get("totac")
                    samt = settletotal.get("totloan")
                    semi = settletotal.get("totemi")

                    emidep = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount')+Sum('latefee'),0))
                    
                    emiac = emidep.get("totac")
                    emiamt = emidep.get("totamt")

                    allr = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode).select_related('master')
                    for all in allr:
                        if all.amount >= all.master.apploanemi:
                            all.flag="Y"
                        else:
                            all.flag="N"
                        all.save()

                    allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A')).order_by('colldaynum','applastemidepdate')

                    for all in allnr:
                        if all.appemiduedate > loginrundate:
                            all.delaydays1 = 2
                        else:
                            all.delaydays1 = 1
                        all.save()

                    allr = Loantrans.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).select_related('master').order_by('date','id')
                    #allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(appemiduedate__lte=ftodate)).order_by('rpersonname', 'colldaynum')
                    allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A')).order_by('rpersonname', 'colldaynum')

                    #balac = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A') & Q(appemiduedate__lte=ftodate)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))
                    balac = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(status='A')).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

                    bac = balac.get("totac")
                    bamt = balac.get("totloan")
                    bemi = balac.get("totemi")
        
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'emiac':emiac,
                            'emiamt':emiamt,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'tac':tac,
                            'tamt':tamt,
                            'temi':temi,
                            'dac':dac,
                            'damt':damt,
                            'demi':demi,
                            'sac':sac,
                            'samt':samt,
                            'semi':semi,
                            'bac':bac,
                            'bemi':bemi,
                            'allr': allr,
                            'allnr':allnr,
                            'dueac': dueac,
                            'totalac':totalac,
                            }
        
                    return render(request, 'admssapp/emidepositreportdashboardshow.html' , context)
    
 


##########################
####  NEW LOAN REPORT ####
##########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def newloanreport(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate    
         loginstatus = ll.status
         currdate = date.today()



         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                #ffromdate = ll.rundate
                #ftodate = ll.rundate
                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        }

            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          
        
                

                    nac = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    namt = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    nemi = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                    allr = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).order_by('apploandate','id')

                    newloanac = nac.get("total")
                    newloanamt = namt.get("total")
                    newloanemi = nemi.get("total")
                    
                
                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()
            
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'newloanac':newloanac,
                            'newloanamt':newloanamt,
                            'newloanemi':newloanemi,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'allr': allr,
                            }
                    
        
                    return render(request, 'admssapp/newloanreportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/newloanreport.html' , context)

#####################################
####  DASHREPORT NEW LOAN REPORT ####
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardnewloanreport(request):

             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()


             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate
            
                    allr = Loanmaster.objects.filter(apploandate__month=loginrundate.month,apploandate__year=loginrundate.year,locationcode=loginlocationcode).order_by('apploandate','id')
                    nac = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year=loginrundate.year,locationcode=loginlocationcode,status="A").aggregate(total = Count("loanid"))
                    namt = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year=loginrundate.year,locationcode=loginlocationcode,status="A").aggregate(total = Sum("apploanamt"))
                    nemi = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year=loginrundate.year,locationcode=loginlocationcode,status="A").aggregate(total = Sum("apploanemi"))

            
            
                    newloanac = nac.get("total")
                    newloanamt = namt.get("total")
                    newloanemi = nemi.get("total")
                    
        
                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")

                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                        
                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'newloanac':newloanac,
                            'newloanamt':newloanamt,
                            'newloanemi':newloanemi,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'allr': allr,
                            }
        
                    return render(request, 'admssapp/newloanreportshow.html' , context)
            

#############################
#### SETTLED LOAN REPORT ####
#############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def settledloanreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate    
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                ffromdate = ll.rundate
                ftodate = ll.rundate
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        }

            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          
        

                    sac = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    samt = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    semi = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                    allr = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode).order_by('apploansettlementdate')

                    settledloanac = sac.get("total")
                    settledloanamt = samt.get("total")
                    settledloanemi = semi.get("total")
                    
                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'settledloanac':settledloanac,
                            'settledloanamt':settledloanamt,
                            'settledloanemi':settledloanemi,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'allr': allr,
                            }

                    return render(request, 'admssapp/settledloanreportshow.html' , context)
            
                else:

                    return render(request, 'admssapp/settledloanreport.html' , context)


#########################################
####  DASHREPORT SETTLED LOAN REPORT ####
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardsettledloanreport(request):

             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()


             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                 return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate
        
                    sac = Loanmaster.objects.filter(apploansettlementdate__month=loginrundate.month,apploansettlementdate__year=loginrundate.year,locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    samt = Loanmaster.objects.filter(apploansettlementdate__month=loginrundate.month,apploansettlementdate__year=loginrundate.year,locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    semi = Loanmaster.objects.filter(apploansettlementdate__month=loginrundate.month,apploansettlementdate__year=loginrundate.year,locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))
                    allr = Loanmaster.objects.filter(apploansettlementdate__month=loginrundate.month,apploansettlementdate__year=loginrundate.year,locationcode=loginlocationcode).order_by('apploansettlementdate')

                    settledloanac = sac.get("total")
                    settledloanamt = samt.get("total")
                    settledloanemi = semi.get("total")
                    
                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")

                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #.
                    # ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'settledloanac':settledloanac,
                            'settledloanamt':settledloanamt,
                            'settledloanemi':settledloanemi,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'allr': allr,
                            }
                    
        
                    return render(request, 'admssapp/settledloanreportshow.html' , context)

    



############################
##### NEAR SETTLEMENT  #####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def nearsettlereport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                ffromdate = ll.rundate
                ftodate = ll.rundate
        

                allr =  Loanmaster.objects.filter(status="A")    
                for all in allr:
                    delaydays1 = ((all.apploanamt + all.apploanint) -  all.apptotalrecamt)/all.apploanemi
                    all.delaydays1 = delaydays1
                    all.apploandueamt = all.apploanamt + all.apploanint
                    #all.save()

                    delta = loginrundate - all.apploandate
                    all.delaydays2 = delta.days
        
                    all.apploanbalamt = all.apploandueamt - all.apptotalrecamt
                    all.save()


                    
                lac = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Count('loanid'),0))
                lamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanamt'),0))
                lemi = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanemi'),0))


                floanac = lac.get("total")
                floanamt = lamt.get("total")
                floanemi = lemi.get("total")
                
                allr = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A")
                for x in allr:
                    floanid = x.loanid
                    fapploanbalamt = x.apploanamt + x.apploanint - x.apptotalrecamt
                    if fapploanbalamt < 0:
                        x.apploanbalamt = 0
                    x.save()

                allr = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).order_by('delaydays1')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'floanac':floanac,
                        'floanamt':floanamt,
                        'floanemi':floanemi,
                        'allr': allr,
                            }
                    
        
                return render(request, 'admssapp/nearsettlereport.html' , context)


#####################
#### LOAN LEDGER ####
#####################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanledger(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('loanid','apploandate')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }

            
                if request.method == "POST" and 'show' in request.POST:
                    fapploanid = request.POST.get('loanidname')
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))
                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid
                    fapploanamt = loanmast.apploanamt
                    fapploandate = loanmast.apploandate
                    fapploantenr = loanmast.apploantenr
                    delta = loginrundate - loanmast.apploandate
                    fapploandays = delta.days
                    fappshoplocation = loanmast.appshoplocation
                    fappoccupation =  loanmast.appoccupation

                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint

                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)


                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint
                    fapptotalbalamt =loanmast.apploanamt + loanmast.apploanint - loanmast.apptotalrecamt

                    latefee = int((loanmast.apploanamt/1000) * fdelaydays)                          

                    acurrdueamt = 0
                    afcurrdueamt = 0
                    afexcessint = 0
                    fappbalamt = 0
                
                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue,  fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin = updatetrans(fapploanid, loginlocationcode, loginrundate)


                    foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)

                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'loanled':loanled,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploandays':fapploandays,
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'loanledsumm':loanledsumm,
                            'ftotalemidue':ftotalemidue,
                            'fcurremidue':fcurremidue,
                            'fcurremidone':fcurremidone,
                            'fcurremibal':fcurremibal,
                            'fcurroverdue':fcurroverdue,
                            'totaldelaydays':totaldelaydays,
                            'foverdueamt':foverdueamt,
                            }

                    return render(request,'admssapp/loanledgershow.html' , context)


                elif request.method == "POST" and 'pdf' in request.POST:
                    fapploanid = request.POST.get('loanidname')
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)

                    fappname = loanmast.appname
                    fapploanid = loanmast.loanid
                    fapploanamt = loanmast.apploanamt
                    fapploandate = loanmast.apploandate
                    fapploantenr = loanmast.apploantenr
                    fapploanemi = loanmast.apploanemi
                    delta = loginrundate - loanmast.apploandate
                    fapploandays = delta.days
                    fappshoplocation = loanmast.appshoplocation
                    fappshopadd = loanmast.appshopadd

                    fappoccupation =  loanmast.appoccupation
                    fapppresentadd = loanmast.apppresentadd
                    fapppresentaddcity = loanmast.apppresentaddcity
                    fappmobileno = loanmast.appmobileno
                    fcoappname = loanmast.coappname
                

                    fapptotalrecamt = loanmast.apptotalrecamt
                    fapptotaldueamt = loanmast.apploanamt + loanmast.apploanint

                    fstatus = loanmast.status
                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt,fcaldepdate,totaldelaydays  = update(fapploanid, loginlocationcode, loginrundate)

                    if fstatus == "A":
                        fapploanstatus="Active"
                    else:
                        fapploanstatus="Closed"

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate':currdate,
                            'loginstatus':loginstatus,
                            'loanled':loanled,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploandays':fapploandays,
                            'fapploanemi':fapploanemi,
                            'fapploanstatus':fapploanstatus,
                            'fappshoplocation':fappshoplocation,
                            'fappshopadd':fappshopadd,
                            'fappoccupation':fappoccupation,
                            'fapppresentadd':fapppresentadd,
                            'fapppresentaddcity':fapppresentaddcity,
                            'fappmobileno':fappmobileno,
                            'fcoappname':fcoappname,
                            'fapploanstatus':fapploanstatus,
                            'fstatus':fstatus,
                            'fcoappname':fcoappname,
                            }

                    pdf = render_to_pdf('admssapp/loanledgerpdf.html', context)
                    return HttpResponse(pdf, content_type='application/pdf')

                else:
                    return render(request, 'admssapp/loanledger.html' , context)


################################
#### EMI Default List ####
################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emidefaultreport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A").order_by('loanid', 'apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
                
                print("##################")
                print(request.method)
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')   
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


                    fdate = ll.rundate

                    last_14_days = loginrundate - timedelta(days=14)
                    last_37_days = loginrundate - timedelta(days=37)
                    last_7_days = loginrundate - timedelta(days=7)
                    last_28_days = loginrundate - timedelta(days=28)
                    
                    ffromdate = last_14_days
                    ftodate = ll.rundate

                    all_loans = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_14_days,appemiduedate__lt=last_37_days , status="A").order_by('applastemidepdate')


                    for loanmast in all_loans:
                        fapploanid = loanmast.loanid   # assuming field name is loanid

                        loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                        loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

                        loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')

                        fcoappname = loanmast.coappname
                        fcoappmobileno = loanmast.coappmobileno
                        fcoapprelation = loanmast.coapprelation
                        fguarname = loanmast.guarname
                        fguarmobileno = loanmast.guarmobileno
                        fguarrelation = loanmast.guarrelation

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
                        
                        ftenrexpireon = fapploandate + timedelta(days=fapploantenr)

                        

                        acurrdueamt = 0
                        afcurrdueamt = 0
                        afexcessint = 0
                        
                        fappbalamt = 0
                    
                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue,  fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin= updatetrans(fapploanid, loginlocationcode, loginrundate)

                        flatefees = loanledsumm1.get("totlatefee")

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)  
                        foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                        ftotaldueamt = fcurrdueamt + foverdueamt - flatefees
                        loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))                    
                        
                        #scheme fapptotalbalamt  
                        #with int fcurrdueamt
                        #with (late ftotaldueamt+latefee)
                        
                        loanmast.duescheme = fapptotalbalamt
                        loanmast.duewithint = fcurrdueamt
                        loanmast.duewithlate = (ftotaldueamt+latefee)
                        loanmast.save()
                        print(loanmast.loanid)
                        
                        all_loans = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_14_days,appemiduedate__lt=last_37_days , status="A").order_by('applastemidepdate')

                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('emidefaultreport')
                        writer = csv.writer(response)
                        writer.writerow(['loanid',
                                          'appname',
                                          'apploanemi',
                                          'loanamt',
                                          'apploandt',
                                          'applastemidepdate',
                                          'duescheme',
                                          'duewithint',
                                          'duewithlate',
                                          'appmobileno',
                                          'coappname',
                                          'coappmobileno',
                                          'coapprelation',
                                          'guarname',
                                          'guarmobileno',

                                          ])

                        for user in all_loans:
                            writer.writerow([user.loanid,
                                             user.appname,
                                             user.apploanemi,
                                             user.apploanamt,
                                             user.apploandate,
                                             user.applastemidepdate,
                                             user.duescheme,
                                             user.duewithint,
                                             user.duewithlate,
                                             user.appmobileno,
                                             user.coappname,
                                             user.coappmobileno,
                                             user.coapprelation,
                                             user.guarname,
                                             user.guarmobileno,
                                             ])

                        return response


                else:

                        return render(request, 'admssapp/emidefaultreport.html' , context)



#################################################
#################################################

################################
#### LOAN LEDGER SETTLEMENT ####
################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanledgersettlement(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").order_by('appname','apploandate')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A").order_by('loanid', 'apploandate')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'nname':nname,
                        'nloanid':nloanid,
                        }
                
            
                if request.method == "POST" and 'show' in request.POST:
                    
 
                    fapploanid = request.POST.get('loanidname')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))


                    fcoappname = loanmast.coappname
                    fcoappmobileno = loanmast.coappmobileno
                    fcoapprelation = loanmast.coapprelation
                    fguarname = loanmast.guarname
                    fguarmobileno = loanmast.guarmobileno
                    fguarrelation = loanmast.guarrelation

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

                    acurrdueamt = 0
                    afcurrdueamt = 0
                    afexcessint = 0
                    
                    fappbalamt = 0
                
                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays,fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue,  fappbalamt, fapptotalrecamt, fapptotalrecamt, fapptotaldueamt,fapptotalbalamt,balprin= updatetrans(fapploanid, loginlocationcode, loginrundate)


                    latefee = int((loanmast.apploanamt/1000) * fdelaydays)  
                    foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                    ftotaldueamt = fcurrdueamt + foverdueamt - flatefees
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))                    

                         

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate':currdate,
                            'loginstatus':loginstatus,
                            'fappname':fappname,
                            'fcoappname':fcoappname,
                            'fcoappmobileno':fcoappmobileno,
                            'fcoapprelation':fcoapprelation,
                            'fguarname':fguarname,
                            'fguarrelation':fguarrelation,
                            'fguarmobileno':fguarmobileno,
                            'fappmobileno':fappmobileno,
                            'fcolldaychar':fcolldaychar,
                            'fapploanid':fapploanid,
                            'fapptotalrecamt':fapptotalrecamt,
                            'fapptotaldueamt':fapptotaldueamt,
                            'fapptotalbalamt':fapptotalbalamt,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fint':fint,
                            'fexcessint':fexcessint,
                            'afexcessint':afexcessint,
                            'fcurrdueamt':fcurrdueamt,
                            'afcurrdueamt':afcurrdueamt,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'loanled':loanled,
                            'loanledsumm':loanledsumm,
                            'ftotalemidue':ftotalemidue,
                            'fcurremidue':fcurremidue,
                            'fcurremidone':fcurremidone,
                            'fcurremibal':fcurremibal,
                            'fcurroverdue':fcurroverdue,
                            'ftenuoverdue': ftenuoverdue,
                            'foverdueamt':foverdueamt,
                            'fapplifeinsurdate':fapplifeinsurdate,
                            'fapplifeinsuruptodate':fapplifeinsuruptodate,
                            'ftotaldueamt':ftotaldueamt,
                            'frpersonname':frpersonname,
                            'fassociatename':fassociatename,
                            'fadminpersonname':fadminpersonname,
                            'flatefees':flatefees,
                            'fcaldepamt':fcaldepamt,
                            'fcaldepdate':fcaldepdate,
                            'fappbalamt':fappbalamt,
                            'fcaldays':fcaldays,
                            'ftenrexpireon':ftenrexpireon,
                            'totaldelaydays':totaldelaydays,
                            'fdelaydays':fdelaydays,    
                            'latefee':latefee,                        
                                }

                    return render(request, 'admssapp/loanledgersettlementshow.html' , context)
            
                else:

                    return render(request, 'admssapp/loanledgersettlement.html' , context)



#################################################
#################################################






############################
#### TRANSACTION REPORT ####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def transreport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in (['B', 'A']):
             return HttpResponseRedirect('/login')
         else:


                ffromdate = ll.rundate
                ftodate = ll.rundate
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        }

                
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')    

                    fffromdate = ffromdate      
                    fftodate = ftodate

                    #### CASH IN HAND ####

                    opcc = Opclcashbank.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).order_by('date')
                    clcc = Opclcashbank.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode).order_by('-date')

                    ffromdate = opcc[0].date
                    ftodate = clcc[0].date

                    opc = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ffromdate).order_by('bankac')
                    clc = Opclcashbank.objects.filter(locationcode=loginlocationcode, date=ftodate).order_by('bankac')

            
                    if opc.count() == 0 or clc.count() == 0:
                        
                            loguserid = request.session['loguserid']
                            ll=Locationlogin.objects.get(user=loguserid)
                
                            loginlocationcode=ll.locationcode
                            loginlocationname=ll.locationname
                            loginrundate=ll.rundate
                            ffromdate = ll.rundate
                            ftodate = ll.rundate
                            error = 'From or To Date is Not A Working Day.'

                            return render(request, 'admssapp/transreport.html' , context)

                    opcash = opc[0]
                    clcash = clc[0]
                    

                    #### CASH AT BANK ####

                    opbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ffromdate)
                    clbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ftodate)


                    Opcltmp.objects.all().delete()

                    for op in opbank:
                        mlocationcode=op.locationcode
                        mlocationname=op.locationname
                        mbankac = op.bankac
                        mbankacname = op.bankacname
                        mbankcode=op.bankcode
                        mbankname=op.bankname
                        mbankbranch=op.bankbranch
                        mbankifsc = op.bankifsc
                        mopbank = op.opbank
                        mopcash = op.opcash
                        mopdate = op.date

                        opbk = Opcltmp(locationcode=mlocationcode,
                                locationname=mlocationname,
                                date=mopdate,
                                bankac=mbankac,
                                bankacname=mbankacname,
                                bankcode=mbankcode,
                                bankname=mbankname,
                                bankbranch=mbankbranch,
                                bankifsc=mbankifsc,
                                opbank=mopbank,
                                opcash=mopcash)
                        opbk.save()

                    for cl in clbank:
                        mlocationcode=cl.locationcode
                        mlocationname=cl.locationname
                        mbankac = cl.bankac
                        mbankacname = cl.bankacname
                        mbankcode=cl.bankcode
                        mbankname=cl.bankname
                        mbankbranch=cl.bankbranch
                        mbankifsc = cl.bankifsc
                        mclbank = cl.clbank
                        mclcash = cl.clcash


                        bankrec = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=mbankac,transcd=mbankcode,drcr="D").aggregate(total=Coalesce(Sum('amount'),0))
                        bankpmt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=mbankac,transcd=mbankcode,drcr="C").aggregate(total=Coalesce(Sum('amount'),0))
                    
                        bankdep = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=mbankac,transcd=mbankcode,drcr="D",chequeno='CASH').aggregate(total=Coalesce(Sum('amount'),0))


                        mbankrec = bankrec.get("total")
                        mbankpmt = bankpmt.get("total")
                        
                        bankrec = mbankrec
                        bankpmt = mbankpmt


                        cashrec = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,mode='CASH',drcr="C").aggregate(total=Coalesce(Sum('amount'),0))
                        cashpmt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,mode='CASH',drcr="D").aggregate(total=Coalesce(Sum('amount'),0))

                        mcashrec = cashrec.get("total")
                        mcashpmt = cashpmt.get("total")

                        cashrec = mcashrec   #+ mbankpmt
                        cashpmt = mcashpmt   #+ mbankrec

                        bankdep = bankdep.get("total")
                               
                    
                        opcl = Opcltmp.objects.get(bankac=mbankac)
                        opcl.clbank = mclbank
                        opcl.clcash = mclcash
                        opcl.bankpmt = mbankpmt
                        opcl.bankrec = mbankrec

                        opcl.save()
                        
                        

                    opcl = Opcltmp.objects.all().order_by('-opbank')
            
                    for op in opcl:
                        opcash = op.opcash
                        clcash = op.clcash



                    nac = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Count('loanid'),0))
                    namt = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    nemi = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanemi'),0))

                    pamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3014').aggregate(total=Coalesce(Sum('amount'),0))
        
                    sac = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Count('loanid'),0))
                    samt = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    semi = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanemi'),0))


                    eac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    eamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))
                    

                    newac = nac.get("total")
                    newamt = namt.get("total")
                    newemi = nemi.get("total")
                    procamt = pamt.get("total")

                    settleac = sac.get("total")
                    settleamt = samt.get("total")
                    settleemi = semi.get("total")


                    emiac = eac.get("total")
                    emiamt = eamt.get("total")

                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()


                    db = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').aggregate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))
                    dblist = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').values('transcd','transnm').annotate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))

                    totalentry =  db.get("totalac")
                    totalamount =  db.get("totalamt")

                
                    fddmmyyyy = fffromdate[8:10:1] + "-" + fffromdate[5:7:1] + "-" + fffromdate[0:4:1]
                    tddmmyyyy = fftodate[8:10:1] + "-" + fftodate[5:7:1] + "-" + fftodate[0:4:1]
                    

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate':currdate,
                            'loginstatus':loginstatus,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'fddmmyyyy':fddmmyyyy,
                            'tddmmyyyy':tddmmyyyy,
                            'newac':newac,
                            'newamt':newamt,
                            'newemi':newemi,
                            'procamt':procamt,
                            'settleac':settleac,
                            'settleamt':settleamt,
                            'settleemi':settleemi,
                            'emiac':emiac,
                            'emiamt':emiamt,
                            'opcash':opcash,
                            'clcash':clcash,
                            'bankdep':bankdep,
                            'cashrec':cashrec,
                            'cashpmt':cashpmt,
                            'bankrec':bankrec,
                            'bankpmt':bankpmt,
                            'opcl':opcl,
                            'dblist':dblist,
                            'totalentry':totalentry,
                            'totalamount':totalamount,
                            }
        
                    return render(request, 'admssapp/transreportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/transreport.html' , context)



############################
##### LOAN STATISTICS ######
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanstatistics(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")
                #ffromdate = ll.rundate
                #ftodate = ll.rundate
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        }

                
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          


                    #### CASH IN HAND ####

                    opc = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ffromdate)
                    clc = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ftodate)

                    for a in opc:
                        opcash = a.opcash

                    for a in clc:
                        clcash = a.clcash
                    

                    #### CASH AT BANK ####

                    opbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ffromdate)
                    clbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=ftodate)


                    Opcltmp.objects.all().delete()

                    for op in opbank:
                        mlocationcode=op.locationcode
                        mlocationname=op.locationname
                        mbankac = op.bankac
                        mbankacname = op.bankacname
                        mbankcode=op.bankcode
                        mbankname=op.bankname
                        mbankbranch=op.bankbranch
                        mbankifsc = op.bankifsc
                        mopbank = op.opbank
                        mopcash = op.opcash
                        mopdate = op.date

                        opbk = Opcltmp(locationcode=mlocationcode,
                                locationname=mlocationname,
                                date=mopdate,
                                bankac=mbankac,
                                bankacname=mbankacname,
                                bankcode=mbankcode,
                                bankname=mbankname,
                                bankbranch=mbankbranch,
                                bankifsc=mbankifsc,
                                opbank=mopbank,
                                opcash=mopcash)
                        opbk.save()

                    for cl in clbank:
                        mlocationcode=cl.locationcode
                        mlocationname=cl.locationname
                        mbankac = cl.bankac
                        mbankacname = cl.bankacname
                        mbankcode=cl.bankcode
                        mbankname=cl.bankname
                        mbankbranch=cl.bankbranch
                        mbankifsc = cl.bankifsc
                        mclbank = cl.clbank
                        mclcash = cl.clcash

                        bankrec = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=mbankac,transcd=mbankcode,drcr="D").aggregate(Sum('amount'))
                        bankpmt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=mbankac,transcd=mbankcode,drcr="C").aggregate(Sum('amount'))

                        mbankrec = bankrec.get("amount__sum")
                        mbankpmt = bankpmt.get("amount__sum")
        
                                
                    opcl = Opcltmp.objects.all()
                    for op in opcl:
                        opcash = op.opcash
                        clcash = op.clcash
                            

                    nac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3010').aggregate(total=Coalesce(Count('loanid'),0))
                    namt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3010').aggregate(total=Coalesce(Sum('amount'),0))
                    pamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3014').aggregate(total=Coalesce(Sum('amount'),0))

                    newac = nac.get("total")
                    newamt = namt.get("total")
                    procamt = pamt.get("total")


                    nmac = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    nmamt = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    nmemi = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                    mnewac = nmac.get("total")
                    mnewamt = nmamt.get("total")
                    mnewemi = nmemi.get("total")

                    naacemi = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Count('loanid'),0))
                    naamtemi = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanemi'),0))

                    activeac = naacemi.get("total")
                    activeamt = naamtemi.get("total")

            
                    eac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    eamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))
                
                    emiac = eac.get("total")
                    emiamt = eamt.get("total")

                    cac = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Count('loanid'),0))
                    camt = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    cemi = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanemi'),0))

                    mcac = cac.get("total")
                    mcamt = camt.get("total")
                    mcemi = cemi.get("total")

                    eac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    epamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3019']).aggregate(total=Coalesce(Sum('amount'),0))
                    eiamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3012']).aggregate(total=Coalesce(Sum('amount'),0))
                    elamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3013']).aggregate(total=Coalesce(Sum('amount'),0))

                    collemi = Daybook.objects.filter(date__range=(ffromdate,ftodate), locationcode=loginlocationcode, transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname','personcode','personname').annotate(collamt=Coalesce(Sum('amount'),0)).annotate(cashamt=Sum('amount',filter=Q(mode__in=['CASH']))).annotate(bankamt=Sum('amount',filter=Q(mode__in=['BANK']))).order_by('-collamt')
                    collsumm = Daybook.objects.filter(date__range=(ffromdate,ftodate), locationcode=loginlocationcode, transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname').annotate(collamt=Coalesce(Sum('amount'),0)).annotate(cashamt=Sum('amount',filter=Q(mode__in=['CASH']))).annotate(bankamt=Sum('amount',filter=Q(mode__in=['BANK']))).order_by('-collamt')

                    if loginlocationcode == '1001': 
                        #eprinamt = epamt.get("total")
                        #eintamt = eiamt.get("total")
                        #elatefee = elamt.get("total")

                        eintamt = int(eiamt.get("total")*.80)
                        elatefee = int(elamt.get("total")*.50)
                        eprinamt = emiamt - eintamt - elatefee
                    else:
                        eprinamt = epamt.get("total")
                        eintamt = eiamt.get("total")
                        elatefee = elamt.get("total")




                    nlamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    niamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanint'),0))

                    ntramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apptotalrecamt'),0))
                    npramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('appprinrecamt'),0))
                    niramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('appintrecamt'),0))

                    mloanamt = nlamt.get("total")
                    mintamt = niamt.get("total")

                    mrecamt = ntramt.get("total")
                    mpramt = npramt.get("total")
                    miramt = niramt.get("total")

                    ntotdueamt = mloanamt + mintamt - mrecamt
                    nprindue = mloanamt - mpramt
                    nintdue = mintamt - miramt

                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()


                    ##### NEAR SETTLE ######
                    allr =  Loanmaster.objects.filter(status="A")    
                    for all in allr:
                        delaydays1 = ((all.apploanamt + all.apploanint) -  all.apptotalrecamt)/all.apploanemi
                        all.delaydays1 = delaydays1
                        all.apploandueamt = all.apploanamt + all.apploanint
                        all.save()
        
                        all.apploanbalamt = all.apploandueamt - all.apptotalrecamt
                        all.save()


                    
                    lac = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Count('loanid'),0))
                    lamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    lemi = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanemi'),0))


                    Ncloanac = lac.get("total")
                    Ncloanamt = lamt.get("total")
                    Ncloanemi = lemi.get("total")

                    allr = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).order_by('delaydays1')

                    fddmmyyyy = ffromdate[8:10:1] + "-" + ffromdate[5:7:1] + "-" + ffromdate[0:4:1]
                    tddmmyyyy = ftodate[8:10:1] + "-" + ftodate[5:7:1] + "-" + ftodate[0:4:1]

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate':currdate,
                            'loginstatus':loginstatus,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'fddmmyyyy':fddmmyyyy,
                            'tddmmyyyy':tddmmyyyy,
                            'newac':newac,
                            'newamt':newamt,
                            'mnewac':mnewac,
                            'mnewamt':mnewamt,
                            'mnewemi':mnewemi,
                            'procamt':procamt,
                            'mcac':mcac,
                            'mcamt':mcamt,
                            'mcemi':mcemi,
                            'activeac':activeac,
                            'activeamt':activeamt,
                            'mcemi':mcemi,
                            'emiac':emiac,
                            'emiamt':emiamt,
                            'eprinamt':eprinamt,
                            'eintamt':eintamt,
                            'elatefee':elatefee,
                            'mloanamt':mloanamt,
                            'ntotdueamt':ntotdueamt,
                            'nprindue':nprindue,
                            'nintdue':nintdue,
                            'Ncloanac':Ncloanac,
                            'Ncloanamt':Ncloanamt,
                            'Ncloanemi':Ncloanemi,
                            'collemi':collemi,
                            'collsumm':collsumm,
                            }


                    return render(request, 'admssapp/loanstatisticsreportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/loanstatisticsreport.html' , context)


#######################################
##### COMPRATIVE LOAN STATISTICS ######
#######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def comprativeloanstatistics(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                #ffromdate = ll.rundate
                #ftodate = ll.rundate
                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")
                
                lastmonth = loginrundate - relativedelta(months=1)

                
                ffromdatelastmonth = lastmonth.strftime("%Y-%m-01")
                ftolastmonth = lastmonth.strftime("%Y-%m-%d")

                lastyear = loginrundate - relativedelta(months=12)

                ffromdatelastyear = lastyear.strftime("%Y-%m-01")
                ftolastyear = lastyear.strftime("%Y-%m-%d")

                
        
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                        'ffromdatelastmonth':ffromdatelastmonth,
                        'ftolastmonth':ftolastmonth,
                        'ffromdatelastyear':ffromdatelastyear,
                        'ftolastyear':ftolastyear,
                        
                         }

                
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')    
                    
                    myradio = request.POST.get('radiomonth')
                  
                    if myradio == 'radiomonth':
                        ffromdatelastmonth = request.POST.get('fromdatelastmonth')
                        ftodatelastmonth = request.POST.get('todatelastmonth')                         
                    
                    elif myradio == 'radioyear':              
                        ffromdatelastmonth = request.POST.get('fromdatelastyear')
                        ftodatelastmonth = request.POST.get('todatelastyear')                         
                        
                    
                   
                    currmonth = datetime.strptime(ffromdate, '%Y-%m-%d').date().strftime('%B') + "'" +datetime.strptime(ffromdate, '%Y-%m-%d').date().strftime('%Y')
                    prevmonth = datetime.strptime(ffromdatelastmonth, '%Y-%m-%d').date().strftime('%B') + "'" +datetime.strptime(ffromdatelastmonth, '%Y-%m-%d').date().strftime('%Y')

                    

                    nac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3010').aggregate(total=Coalesce(Count('loanid'),0))
                    namt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3010').aggregate(total=Coalesce(Sum('amount'),0))
                    pamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd='3014').aggregate(total=Coalesce(Sum('amount'),0))

                    newac = nac.get("total")
                    newamt = namt.get("total")
                    procamt = pamt.get("total")
                    

                    #### Current Month new Loan ####
                    currnac = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    currnamt = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    currnemi = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                    currnewloan = currnac.get("total")
                    currloanamt = currnamt.get("total")
                    currloanemi = currnemi.get("total")


                    #### Previeus Month new Loan ####
                    prevnac = Loanmaster.objects.filter(apploandate__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode).aggregate(total=Coalesce(Count('loanid'),0))
                    prevnamt = Loanmaster.objects.filter(apploandate__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    prevnemi = Loanmaster.objects.filter(apploandate__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                    prevnewloan = prevnac.get("total")
                    prevloanamt = prevnamt.get("total")
                    prevloanemi = prevnemi.get("total")


                    #### Diff new Loan ####
                    #######################
                    
                    diffnewloan = currnewloan - prevnewloan
                    if prevnewloan !=0:
                        pernewloan = (currnewloan - prevnewloan) *100 / prevnewloan
                        pernewloan = "%0.2f" % pernewloan
                    elif currnewloan !=0:
                        pernewloan = "%0.2f" % 100
                    elif currnewloan == 0:
                        pernewloan = "%0.2f" % 0                    

                    diffloanamt = currloanamt - prevloanamt
                    if prevnewloan !=0:
                        perloanamt = (currloanamt - prevloanamt) *100 / prevloanamt
                        perloanamt = "%0.2f" % perloanamt
                    elif currloanamt !=0:
                        perloanamt = "%0.2f" % 100
                    elif currloanamt ==0:
                        perloanamt = "%0.2f" % 0                        



                    diffnewloanemi = currloanemi - prevloanemi
                    if prevloanemi !=0:
                        perloanemi = (currloanemi - prevloanemi) *100 / prevloanemi
                        perloanemi = "%0.2f" % perloanemi
                    elif currloanemi !=0:
                        perloanemi = "%0.2f" % 100
                    elif currloanemi ==0:
                        perloanemi = "%0.2f" % 0                        

                    #### Settled Loan #### 
                    ######################

                    cac = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Count('loanid'),0))
                    camt = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    cemi = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,status="C").aggregate(total=Coalesce(Sum('apploanemi'),0))

                    mcac = cac.get("total")
                    mcamt = camt.get("total")
                    mcemi = cemi.get("total")

                    
                    
                    #### CURRENT MONTH EMI ####
                    ###########################
            
                    curreac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    curramt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))
                
                    curremiac = curreac.get("total")
                    curremiamt = curramt.get("total")
                    
                    #### PREVIEOUS MONTH EMI ####
            
                    prevac = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    prevamt = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))
                
                    prevemiac = prevac.get("total")
                    prevemiamt = prevamt.get("total")
                    


                    currac = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    currprin = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3011','3019']).aggregate(total=Coalesce(Sum('amount'),0))
                    currint = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3012']).aggregate(total=Coalesce(Sum('amount'),0))
                    currlate = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,transcd__in=['3013']).aggregate(total=Coalesce(Sum('amount'),0))

                    prevac = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                    prevprin = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3011','3019']).aggregate(total=Coalesce(Sum('amount'),0))
                    prevint = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3012']).aggregate(total=Coalesce(Sum('amount'),0))
                    prevlate = Daybook.objects.filter(date__range=(ffromdatelastmonth,ftodatelastmonth),locationcode=loginlocationcode,transcd__in=['3013']).aggregate(total=Coalesce(Sum('amount'),0))



                    collemi = Daybook.objects.filter(date__range=(ffromdate,ftodate), locationcode=loginlocationcode, transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname','personcode','personname').annotate(collamt=Coalesce(Sum('amount'),0)).annotate(cashamt=Sum('amount',filter=Q(mode__in=['CASH']))).annotate(bankamt=Sum('amount',filter=Q(mode__in=['BANK']))).order_by('-collamt')
                    collsumm = Daybook.objects.filter(date__range=(ffromdate,ftodate), locationcode=loginlocationcode, transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname').annotate(collamt=Coalesce(Sum('amount'),0)).annotate(cashamt=Sum('amount',filter=Q(mode__in=['CASH']))).annotate(bankamt=Sum('amount',filter=Q(mode__in=['BANK']))).order_by('-collamt')
                    from django.db.models import  FloatField,F,DecimalField,ExpressionWrapper
                    collrep = Daybook.objects.filter(locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013'],date__range=(ffromdatelastmonth,ftodate)).values('personcode','personname').annotate(prevmonth=Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth)))).annotate(currmonth=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0)).annotate(diff=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0) - Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0)).annotate(per=Case(When(prevmonth=None, then=100), default=((Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0) - Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0))*100)/Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0))).order_by('-currmonth')
                    
                    #collrep = Daybook.objects.filter(locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013'],date__range=(ffromdatelastmonth,ftodate)).values('personcode','personname').annotate(prevmonth=Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth)))).annotate(currmonth=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0)).annotate(diff=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0) - Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0))

                    colltot = Daybook.objects.values('locationcode','locationname').filter(locationcode=loginlocationcode,transcd__in=['3011','3012','3019','3013'],date__range=(ffromdatelastmonth,ftodate)).annotate(prevmonth=Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth)))).annotate(currmonth=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0)).annotate(diff=Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0) - Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0)).annotate(per=((Coalesce(Sum('amount',filter=Q(date__range=(ffromdate,ftodate))),0) - Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0)))*100/Coalesce(Sum('amount',filter=Q(date__range=(ffromdatelastmonth,ftodatelastmonth))),0))


                    if loginlocationcode == '1001': 
                        #eprinamt = epamt.get("total")
                        #eintamt = eiamt.get("total")
                        #elatefee = elamt.get("total")

                        currintamt = int(currint.get("total")*.80)
                        currlatefee = int(currlate.get("total")*.50)
                        currprinamt = curremiamt - currintamt - currlatefee
                        
                        previntamt = int(prevint.get("total")*.80)
                        prevlatefee = int(prevlate.get("total")*.50)
                        prevprinamt = prevemiamt - previntamt - prevlatefee

                    else:

                        currprinamt = currprin.get("total")
                        currintamt = currint.get("total")
                        currlatefee = currlate.get("total")

                        prevprinamt = prevprin.get("total")
                        previntamt = prevint.get("total")
                        prevlatefee = prevlate.get("total")


                    diffemiac = curremiac - prevemiac
                    if prevemiac !=0:
                        peremiac = (curremiac - prevemiac) *100 / prevemiac
                        peremiac = "%0.2f" % peremiac
                    elif curremiac !=0:
                        peremiac = "%0.2f" % 100
                    elif curremiac ==0:
                        peremiac = "%0.2f" % 0                        

                    diffemiamt = curremiamt - prevemiamt
                    if prevemiamt !=0:
                        peremiamt = (curremiamt - prevemiamt) *100 / prevemiamt
                        peremiamt = "%0.2f" % peremiamt
                    elif curremiamt !=0:
                        peremiamt = "%0.2f" % 100
                    elif curremiamt ==0:
                        peremiamt = "%0.2f" % 0

                    diffprinamt = currprinamt - prevprinamt
                    if prevprinamt !=0:
                        perprinamt = (currprinamt - prevprinamt) *100 / prevprinamt
                        perprinamt = "%0.2f" % perprinamt
                    elif currprinamt !=0:
                        perprinamt = "%0.2f" % 100
                    elif currprinamt ==0:
                        perprinamt = "%0.2f" % 0                        

                    diffintamt = currintamt - previntamt
                    if previntamt !=0:
                        perintamt = (currintamt - previntamt) *100 / previntamt
                        perintamt = "%0.2f" % perintamt
                    elif currintamt !=0:
                        perintamt = "%0.2f" % 100
                    elif currintamt ==0:
                        perintamt = "%0.2f" % 0
                        
                    difflatefee = currlatefee - prevlatefee
                    if previntamt !=0:
                        perlatefee = (currlatefee - prevlatefee) *100 / prevlatefee
                        perlatefee = "%0.2f" % perlatefee
                    elif currlatefee !=0:
                        perlatefee = "%0.2f" % 100
                    elif currlatefee ==0:
                        perlatefee = "%0.2f" % 0
                                                

                    nlamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanamt'),0))
                    niamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apploanint'),0))

                    ntramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('apptotalrecamt'),0))
                    npramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('appprinrecamt'),0))
                    niramt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A").aggregate(total=Coalesce(Sum('appintrecamt'),0))

                    mloanamt = nlamt.get("total")
                    mintamt = niamt.get("total")

                    mrecamt = ntramt.get("total")
                    mpramt = npramt.get("total")
                    miramt = niramt.get("total")

                    ntotdueamt = mloanamt + mintamt - mrecamt
                    nprindue = mloanamt - mpramt
                    nintdue = mintamt - miramt

                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()


                    ##### NEAR SETTLE ######
                    ########################
                    
                    allr =  Loanmaster.objects.filter(status="A")    
                    for all in allr:
                        delaydays1 = ((all.apploanamt + all.apploanint) -  all.apptotalrecamt)/all.apploanemi
                        all.delaydays1 = delaydays1
                        all.apploandueamt = all.apploanamt + all.apploanint
                        all.save()
        
                        all.apploanbalamt = all.apploandueamt - all.apptotalrecamt
                        all.save()


                    
                    lac = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Count('loanid'),0))
                    lamt = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanamt'),0))
                    lemi = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).aggregate(total=Coalesce(Sum('apploanemi'),0))


                    Ncloanac = lac.get("total")
                    Ncloanamt = lamt.get("total")
                    Ncloanemi = lemi.get("total")

                    allr = Loanmaster.objects.filter(locationcode=loginlocationcode,status="A", delaydays1__lte=4).order_by('delaydays1')

                    fddmmyyyy = ffromdate[8:10:1] + "-" + ffromdate[5:7:1] + "-" + ffromdate[0:4:1]
                    tddmmyyyy = ftodate[8:10:1] + "-" + ftodate[5:7:1] + "-" + ftodate[0:4:1]


                    
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'currdate':currdate,
                            'loginstatus':loginstatus,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'ffromdatelastmonth':ffromdatelastmonth,
                            'ftodatelastmonth': ftodatelastmonth,
                            'fddmmyyyy':fddmmyyyy,
                            'tddmmyyyy':tddmmyyyy,
                            'currmonth':currmonth,
                            'prevmonth':prevmonth,
                            'currnewloan':currnewloan,
                            'currloanamt':currloanamt,
                            'currloanemi':currloanemi,
                            'prevnewloan':prevnewloan,
                            'prevloanamt':prevloanamt,
                            'prevloanemi':prevloanemi,
                            'pernewloan':pernewloan,
                            'perloanamt':perloanamt,
                            'perloanemi':perloanemi,
                            'curremiac':curremiac,
                            'curremiamt':curremiamt,
                            'currprinamt':currprinamt,
                            'currintamt':currintamt,
                            'currlatefee':currlatefee,
                            'prevemiac':prevemiac,
                            'prevemiamt':prevemiamt,
                            'prevprinamt':prevprinamt,
                            'previntamt':previntamt,
                            'prevlatefee':prevlatefee,
                            'peremiac':peremiac,
                            'peremiamt':peremiamt,
                            'perprinamt':perprinamt,
                            'perintamt':perintamt,
                            'perlatefee':perlatefee,
                            'collrep':collrep,
                            'colltot':colltot
                            }


                    return render(request, 'admssapp/comprativeloanstatisticsreportshow.html' , context)
            
                else:
                    return render(request, 'admssapp/comprativeloanstatisticsreport.html' , context)






#############################################
###### EMI COLLECTOR COLLECTION REPORT ######
#############################################
@login_required(login_url='login')
@never_cache
def collemireportbranch(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user_id=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                allcolldata = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').order_by('rpersoncode')
            
                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0)).order_by('rpersoncode')
                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode,status='N').values('locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'),0))
                    

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allcolldata': allcolldata,
                        'collsumm':collsumm,
                        'collsummall':collsummall,
                            }
        
                return render(request, 'admssapp/collemireportbranch.html' , context)
            



#########################################
##### EMI COLLECTOR DEV EXP REPORT ######
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emicollectorreport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")

                    emicoll = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')
        
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'emicoll': emicoll,
                            }

                    if request.method == "POST":
                            ffromdate = request.POST.get('fromdate')
                            ftodate=request.POST.get('todate')     
                            fcollcode=request.POST.get('collcode')   

                    
                            allrecord = Daybook.objects.values('personcode','personname').filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3013','3019']).annotate(totemi=Sum('amount',filter=Q(transcd__in=['3011','3012','3013','3019']))).annotate(totint=Sum('amount',filter=Q(transcd__in=['3012','3013']))).order_by('personcode')

                            allamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013']).aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))
                            indiamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013'],loanid__startswith='I').aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))
                            groupamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013'],loanid__startswith='G').aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))

                            intamtindi = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, personcode=fcollcode, transcd__in=[
                                                            '3012', '3013'], loanid__startswith='I').aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount'), 0))
                
                            intamtgroup = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, personcode=fcollcode, transcd__in=[
                                                            '3012', '3013'], loanid__startswith='G').aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount'), 0))

                            totac = allamt.get("totac")
                            totamt = allamt.get("totamt")
 
                            indiac = indiamt.get("totac")
                            indiamt = indiamt.get("totamt")

                            groupac = groupamt.get("totac")
                            groupamt = groupamt.get("totamt")

                            intindiac = intamtindi.get("totac")
                            intindiamt = intamtindi.get("totamt")
                            intgroupac = intamtgroup.get("totac")
                            intgroupamt = intamtgroup.get("totamt")

                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'loginstatus':loginstatus,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'allrecord':allrecord,
                                    'totamt':totamt,
                                    'indiamt':indiamt,
                                    'groupamt':groupamt,
                                    'intindiamt':intindiamt,
                                    'intgroupamt':intgroupamt,
                                    }
                            return render(request, 'admssapp/emicollectorreportshow.html' , context)

        
                    return render(request, 'admssapp/emicollectorreport.html' , context)





#################################
######## GROUP WISE LIST ########
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def groupwiselist(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    grouphead = Loanmaster.objects.filter(locationcode=loginlocationcode,loantype="GROUP", status='A').order_by().values('groupleaderloanid','groupleadername','appshoplocation').annotate(totac=Count('loanid'))

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'grouphead':grouphead,              
                            }

                    if request.method == "POST":
                            fgroupleaderloanid = request.POST.get('groupleader')
                    
                            all = Loanmaster.objects.filter(groupleaderloanid=fgroupleaderloanid)
                            for a in all:
                                fapploanid = a.loanid
                                fapploanamt = a.apploanamt
                                fapploanint = a.apploanint
                                fapploandate = a.apploandate
                                fapploantenr = a.apploantenr

                                loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')

                                fdepamt = 0
                                fcaldepamt = a.apptotalrecamt
                                
                                datechk="Y"
                                for b in loanled:
                                    fdepamt = fdepamt + b.amount

                                    if (loginrundate - fapploandate).days > fapploantenr:
                                        if (b.date - fapploandate).days > fapploantenr and datechk == "Y":
                                            fcaldepdate = b.date
                                            fcaldepamt = fdepamt - b.amount
                                            datechk="N"


                                        if datechk=="Y":
                                            fcaldepdate = b.date
                                            fcaldepamt = fdepamt                                    

                                    flastdepdate = b.date    

                                fapptotalrecamt = a.apptotalrecamt
                                fapptotaldueamt = a.apploanamt + a.apploanint
                                fapptotalbalamt = a.apploanamt + a.apploanint - a.apptotalrecamt

                                fappbalamt = a.apploanamt + a.apploanint - fcaldepamt
                                delta = (loginrundate - flastdepdate)
                             
                                fcaldays = int((delta.days)/30)+1
                                fcaldays = fcaldays*30
                                rate = Rate.objects.get(days=360)
                                frate = rate.rate

                                nint = (fappbalamt*(frate))/100
                                fint=round((nint*fcaldays)/360)

                                acurrdueamt = fapploanamt+fapploanint+fint
                                fcurrdueamt = (fapploanamt+fapploanint+fint)-fapptotalrecamt
                                fexcessint = fint
                                
                                totaldays = (loginrundate - a.apploandate).days
                                ftotalemidue = round(float(a.apploantenr/15), 2)
                                fcurremidue = round(float(totaldays/15), 2)
                                if fcurremidue > ftotalemidue:
                                    fcurremidue = ftotalemidue
                                    fcurremidone = round(float(a.apptotalrecamt/a.apploanemi), 2)
                                    fcurremibal = round(float(fcurremidue - fcurremidone), 2)
                                    if fcurremibal < 0:
                                        fcurremibal = 0
                                    fcurroverdue =  int(fcurremibal*a.apploanemi)
                                    if totaldays >= a.apploantenr:
                                        tenuoverdue =  totaldays - a.apploantenr
                                        ftenuoverdue = round(float(tenuoverdue/15), 2)
                                else:
                                    ftenuoverdue = round(float(0), 2)
                                    fcurremibal = round(float(0), 2)
                            
                                foverdueamt = int(fcurremibal * (a.apploanamt/1000) * 7)

                                a.delaydays1 = a.apploanamt + a.apploanint
                                a.delaydays2 = a.apploanamt + a.apploanint - a.apptotalrecamt
                                a.delaydays3 = fexcessint + foverdueamt
                                
                                if a.status=='C':
                                    a.delaydays1 = fapptotalrecamt
                                    a.delaydays2 = 0
                                    a.delaydays3 = 0
                                    
                                    
                                    
                            
                                a.save()


                            #colldaywise = Loanmaster.objects.filter(locationcode=loginlocationcode,groupleaderloanid=fgroupleaderloanid,status='A').values('locationcode','rpersoncode','rpersonname','colldaynum','colldaychar').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).order_by('colldaynum')
                       
           
                            allgrouplist = Loanmaster.objects.filter(locationcode=loginlocationcode,groupleaderloanid=fgroupleaderloanid).order_by('status')
                            summtot = Loanmaster.objects.filter(locationcode=loginlocationcode,groupleaderloanid=fgroupleaderloanid).values('locationcode').annotate(totac=Coalesce(Count('loanid'),0)).annotate(totloan=Coalesce(Sum('apploanamt'),0)).annotate(totemi=Coalesce(Sum('apploanemi'),0)).annotate(totaldue=Coalesce(Sum('delaydays1'),0)).annotate(totalrec=Coalesce(Sum('apptotalrecamt'),0)).annotate(totalbal=Coalesce(Sum('delaydays2'),0)).annotate(totaloverdue=Coalesce(Sum('delaydays3'),0))

                    
                            fgroupleaderloanid = allgrouplist[0].groupleaderloanid
                            fgroupleadername = allgrouplist[0].groupleadername
                            fgrouplocations = allgrouplist[0].appshoplocation

                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'fgroupleaderloanid':fgroupleaderloanid,
                                    'fgroupleadername':fgroupleadername,
                                    'fgrouplocations': fgrouplocations,
                                    'allgrouplist':allgrouplist,
                                    'summtot':summtot,
                                    }
                            return render(request, 'admssapp/groupwiselistshow.html' , context)
        
                    return render(request, 'admssapp/groupwiselist.html' , context)




#########################################
######## EMI COLLECTOR WISE LIST ########
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emicollectorwiselist(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    #ffromdate = loginrundate.strftime("%Y-%m-01")
                    #ftodate = loginrundate.strftime("%Y-%m-%d")
                    emicoll = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')
        
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'emicoll':emicoll,              
                            }

                    if request.method == "POST":
                            frpersoncode = request.POST.get('rperson_name')
                    
                            all = Loanmaster.objects.filter(status="A")
                            for a in all:
                                a.delaydays1 = a.appemiduedate.weekday()
                                if a.applastemidepdate is not None:
                                    delta = loginrundate - a.applastemidepdate
                                else:
                                    delta = loginrundate - a.apploandate 
                            
                                a.delaydays2 = delta.days

                                a.delaydays3 =  (loginrundate - a.apploandate).days

                            
                                a.save()


                            colldaywise = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').values('locationcode','rpersoncode','rpersonname','colldaynum','colldaychar').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).order_by('colldaynum')
                            colltot = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').values('locationcode','rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0))
                            
  
            
                            allemilist = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status="A").order_by('colldaynum','applastemidepdate')
                    
                            frpersonname = allemilist[0].rpersonname
                            frpersoncode = allemilist[0].rpersoncode
                    
                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'allemilist':allemilist,
                                    'frpersoncode':frpersoncode,
                                    'frpersonname':frpersonname,
                                    'colldaywise':colldaywise,
                                    'colltot':colltot,
                                    }
                            return render(request, 'admssapp/emicollectorwiselistshow.html' , context)
        
                    return render(request, 'admssapp/emicollectorwiselist.html' , context)


########################################
######## LOANID ADMIN WISE LIST ########
########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanidadminwiselist(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    #ffromdate = loginrundate.strftime("%Y-%m-01")
                    #ftodate = loginrundate.strftime("%Y-%m-%d")
                    emiadmin = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('adminpersoncode','adminpersonname').distinct().order_by('adminpersonname')
        
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'emiadmin':emiadmin,              
                            }

                    if request.method == "POST":
                            fadminpersoncode = request.POST.get('rperson_name')
                            ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                            ftodate = ffromdate + timedelta(days=5)

                    
                            all = Loanmaster.objects.filter(status="A")
                            for a in all:
                                a.delaydays1 = a.appemiduedate.weekday()
                                if a.applastemidepdate is not None:
                                    delta = loginrundate - a.applastemidepdate
                                    
                                    if a.applastemidepdate >= ffromdate or a.appemiduedate >= ftodate:
                                        a.delaydays3 =  1
                                    else:
                                        a.delaydays3 =  2
                                
                                else:
                                    delta = loginrundate - a.apploandate 
                                    a.delaydays3 =  2
                            
                                a.delaydays2 = delta.days
                            
                                a.save()


                            admintot = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname').filter(locationcode=loginlocationcode,adminpersoncode=fadminpersoncode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0))
                            
                            admindaywise = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname','colldaynum','colldaychar').filter(locationcode=loginlocationcode,adminpersoncode=fadminpersoncode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Sum('apploanemi')).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('colldaynum')
           
                            allemilist = Loanmaster.objects.filter(locationcode=loginlocationcode,adminpersoncode=fadminpersoncode,status="A").order_by('colldaynum','applastemidepdate')
                    
                            fadminpersonname = allemilist[0].adminpersonname
                            fadminpersoncode = allemilist[0].adminpersoncode
                    

                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'allemilist':allemilist,
                                    'fadminpersoncode':fadminpersoncode,
                                    'fadminpersonname':fadminpersonname,
                                    'admindaywise':admindaywise,
                                    'admintot':admintot,
  
                                    }
                            
                            return render(request, 'admssapp/emiadminwiselistshow.html' , context)
        
                    return render(request, 'admssapp/emiadminwiselist.html' , context)



#########################################################
######## LOANID ADMIN PERFORMANCE SUMMARY PERIOD ########
#########################################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanidadminsummary(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    emiadmin = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('adminpersoncode','adminpersonname').distinct().order_by('adminpersonname')

                    context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'loginstatus':loginstatus,
                             'currdate':currdate,
                             'emiadmin':emiadmin,
                                      }

                    if request.method == "POST":
                        fperiod = request.POST.get('reportperiod')
                        if fperiod == 'CurrentWeek':
                            fperiod = 'CurrentWeek'
                            ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                            ftodate = ffromdate + timedelta(days=5)
                            context={'loginlocationcode':loginlocationcode,
                                   'loginlocationname':loginlocationname,
                                   'loginrundate':loginrundate,
                                   'loginstatus':loginstatus,
                                   'currdate':currdate,
                                   'ffromdate':ffromdate,
                                   'ftodate':ftodate,
                                   'fperiod':fperiod,
                                      }           
                            return render(request, 'admssapp/emiadminreportperiodweek.html' , context)                            

                        elif fperiod == 'CurrentMonth':
                            fperiod = 'CurrentMonth'
                            ffromdate = datetime.strptime(loginrundate.strftime("%Y-%m-01"),'%Y-%m-%d').date()
                            ftodate = datetime.strptime(loginrundate.strftime("%Y-%m-%d"),'%Y-%m-%d').date()

                            context={'loginlocationcode':loginlocationcode,
                                   'loginlocationname':loginlocationname,
                                   'loginrundate':loginrundate,
                                   'loginstatus':loginstatus,
                                   'currdate':currdate,
                                   'ffromdate':ffromdate,
                                   'ftodate':ftodate,
                                   'fperiod':fperiod,
                                      }           
                            return render(request, 'admssapp/emiadminreportperiodweek.html' , context)                            

                        elif fperiod == 'SpecificPeriod':
                            fperiod = 'SpecificPeriod'
                            ffromdate = datetime.strptime(loginrundate.strftime("%Y-%m-01"),'%Y-%m-%d').date()
                            ftodate = datetime.strptime(loginrundate.strftime("%Y-%m-%d"),'%Y-%m-%d').date()

                            context={'loginlocationcode':loginlocationcode,
                                   'loginlocationname':loginlocationname,
                                   'loginrundate':loginrundate,
                                   'loginstatus':loginstatus,
                                   'currdate':currdate,
                                   'ffromdate':ffromdate,
                                   'ftodate':ftodate,
                                   'fperiod':fperiod,
                                      }           
                            return render(request, 'admssapp/emiadminreportperiodmonth.html' , context)                            

        
                    return render(request, 'admssapp/emiadminreport.html' , context)
                





#########################################################
######## LOANID ADMIN PERFORMANCE SUMMARY REPORT ########
#########################################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanidadminsummaryreport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate


                    if request.method == "POST":
                        fperiod = request.POST.get('reportperiod')

                        
                        if fperiod == 'CurrentWeek':
                            ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                            ftodate = ffromdate + timedelta(days=5)

                            vfromdate = ffromdate
                            vtodate = ftodate                         

                            all = Loanmaster.objects.filter(status="A")
                            for a in all:
                                a.delaydays1 = a.appemiduedate.weekday()
                                if a.applastemidepdate is not None:
                                    delta = loginrundate - a.applastemidepdate
                                    
                                    if a.applastemidepdate >= ffromdate or a.appemiduedate >= ftodate:
                                        a.delaydays3 =  1
                                    else:
                                        a.delaydays3 =  2
                                
                                else:
                                    delta = loginrundate - a.apploandate 
                 
                                    a.delaydays3 =  2
                            
                                a.delaydays2 = delta.days
                                a.save()



                            admintot = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=(Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid'))).order_by('adminpersonname')
                            adminsumm = Loanmaster.objects.values('locationcode').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid'))
                            admindaywise = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname','colldaynum','colldaychar').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Sum('apploanemi')).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('colldaynum')

                        elif fperiod == 'CurrentMonth':

                            ffromdate = request.POST.get('fromdate')
                            ftodate = request.POST.get('todate')
                            
                            
                            vfromdate = datetime.strptime(ffromdate, '%Y-%m-%d').date()
                            vtodate = datetime.strptime(ftodate, '%Y-%m-%d').date() 

                            all = Loanmaster.objects.filter(status="A")

                            for a in all:
                                floanid=a.loanid

                                
                                dep = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=floanid, date__gte=ffromdate,date__lte=ftodate).values('locationcode','loanid').aggregate(depemi=Coalesce(Count('transid'),0),depamt=Coalesce(Sum('amount'),0))
                                noemi = dep.get("depemi")
                                amtemi = dep.get("depamt")
                                                        
                                count=0
                                if a.appemifreq == "WEEKLY":
                                    for d_ord in range(vfromdate.toordinal(), vtodate.toordinal()+1):
                                        d = date.fromordinal(d_ord)
                                        if (d.weekday() == a.colldaynum):
                                            count += 1
                                        
                                    if noemi >= count:
                                        fdelaydays3 = 1
                                    else:
                                        fdelaydays3 = 2
                                    
                                elif a.appemifreq == "FORTNIGHTLY":
                                    totdays = vtodate.toordinal()-vfromdate.toordinal()+1
                                    count = int(totdays/14)

                                    if noemi >= count:
                                        fdelaydays3 = 1
                                    else:
                                        fdelaydays3 = 2
                                
                                                                
                                a.delaydays3 = fdelaydays3
                                a.save()


                            admintot = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid')).order_by('adminpersonname')
                            adminsumm = Loanmaster.objects.values('locationcode').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid'))
                            admindaywise = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname','colldaynum','colldaychar').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Sum('apploanemi')).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('colldaynum')

                        elif fperiod == 'SpecificPeriod':

                            ffromdate = request.POST.get('fromdate')
                            ftodate = request.POST.get('todate')
                            
                            
                            vfromdate = datetime.strptime(ffromdate, '%Y-%m-%d').date()
                            vtodate = datetime.strptime(ftodate, '%Y-%m-%d').date() 

                            all = Loanmaster.objects.filter(status="A")

                            for a in all:
                                floanid=a.loanid

                                
                                dep = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=floanid, date__gte=ffromdate,date__lte=ftodate).values('locationcode','loanid').aggregate(depemi=Coalesce(Count('transid'),0),depamt=Coalesce(Sum('amount'),0))
                                noemi = dep.get("depemi")
                                amtemi = dep.get("depamt")
                                                        
                                count=0
                                if a.appemifreq == "WEEKLY":
                                    for d_ord in range(vfromdate.toordinal(), vtodate.toordinal()+1):
                                        d = date.fromordinal(d_ord)
                                        if (d.weekday() == a.colldaynum):
                                            count += 1
                                        
                                    if noemi >= count:
                                        fdelaydays3 = 1
                                    else:
                                        fdelaydays3 = 2
                                    
                                elif a.appemifreq == "FORTNIGHTLY":
                                    totdays = vtodate.toordinal()-vfromdate.toordinal()+1
                                    count = int(totdays/14)

                                    if noemi >= count:
                                        fdelaydays3 = 1
                                    else:
                                        fdelaydays3 = 2
                                
                                                                
                                a.delaydays3 = fdelaydays3
                                a.save()


                            admintot = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid')).order_by('adminpersonname')
                            adminsumm = Loanmaster.objects.values('locationcode').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).annotate(percent=Count('loanid',filter=Q(delaydays3__in=[1]))*100/Count('loanid'))
                            admindaywise = Loanmaster.objects.values('locationcode','adminpersoncode','adminpersonname','colldaynum','colldaychar').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Sum('apploanemi')).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('colldaynum')



                        ffromdate = vfromdate
                        ftodate = vtodate
                        context={'loginlocationcode':loginlocationcode,
                                       'loginlocationname':loginlocationname,
                                       'loginrundate':loginrundate,
                                       'loginstatus':loginstatus,
                                       'currdate':currdate,
                                       'ffromdate':ffromdate,
                                       'ftodate':ftodate,
                                       'admindaywise':admindaywise,
                                       'admintot':admintot,
                                       'adminsumm':adminsumm,
                                          }
                            
                        return render(request, 'admssapp/emiadminsummary.html' , context)
        
                
                
############################################
######## COLLECTOR WISE EMI SUMMARY ########
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanidcollectorsummary(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate


                    frpersoncode = request.POST.get('rperson_name')
                    ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                    ffromdategroup = loginrundate - timedelta(days=loginrundate.weekday()+7)
                    ftodate = ffromdate + timedelta(days=5)

                    
                    all = Loanmaster.objects.filter(status="A")
                    for a in all:
                        a.delaydays1 = a.appemiduedate.weekday()
                               
                        if a.applastemidepdate is not None:
                            delta = loginrundate - a.applastemidepdate
                        else:
                            delta = loginrundate - a.apploandate 
                            
                            a.delaydays2 = delta.days
                            a.delaydays3 =  (loginrundate - a.apploandate).days
                                
                            if a.applastemidepdate is not None:
                                if a.loantype == 'INDIVIDUAL':
                                    if a.applastemidepdate >= ffromdate and a.applastemidepdate <= ftodate:
                                        a.delaydays1 = 0
                                        a.delaydays3 = 1
                                        a.flag = 'N'
                                    else:
                                        a.delaydays1 = 1
                                        a.delaydays3 = 2
                                        a.flag = 'Y'
                                else:
                                    a.delaydays1 = 1
                                    a.flag = 'Y'
                                    
                                if a.loantype == 'GROUP':
                                    if a.applastemidepdate >= ffromdategroup  and a.applastemidepdate <= ftodate:
                                        a.delaydays1 = 0
                                        a.delaydays3 = 1
                                        a.flag = 'N'
                                    else:
                                        a.delaydays1 = 1
                                        a.delaydays3 = 2
                                        a.flag = 'Y'
                            else:
                                a.delaydays1 = 1
                                a.delaydays3 = 2
                                a.flag = 'Y'
                       
                            a.save()


                    colltot = Loanmaster.objects.values('locationcode','rpersoncode','rpersonname').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('rpersonname')
                    collsumm = Loanmaster.objects.values('locationcode').filter(locationcode=loginlocationcode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0))
                            
           
                        
                    context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'loginstatus':loginstatus,
                             'currdate':currdate,
                             'ffromdate':ffromdate,
                             'ftodate':ftodate,
                             'colltot' :colltot,
                             'collsumm':collsumm,
                                    }
                    return render(request, 'admssapp/emicollectorsummary.html' , context)
        




#################################################
######## COLLECTOR WISE EMI PENDING LIST ########
#################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emicollectorwisependinglist(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    #ffromdate = loginrundate.strftime("%Y-%m-01")
                    #ftodate = loginrundate.strftime("%Y-%m-%d")
                    emicoll = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')
        
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'emicoll':emicoll,              
                            }

                    if request.method == "POST":
                            frpersoncode = request.POST.get('rperson_name')
                            ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                            ffromdategroup = loginrundate - timedelta(days=loginrundate.weekday()+7)
                            ftodate = ffromdate + timedelta(days=5)

                    
                            all = Loanmaster.objects.filter(status="A")
                            for a in all:
                                a.delaydays1 = a.appemiduedate.weekday()
                               
                                if a.applastemidepdate is not None:
                                    delta = loginrundate - a.applastemidepdate
                                else:
                                    delta = loginrundate - a.apploandate 
                            
                                a.delaydays2 = delta.days
                                a.delaydays3 =  (loginrundate - a.apploandate).days
                                
                                if a.applastemidepdate is not None:
                                    if a.loantype == 'INDIVIDUAL':
                                        if a.applastemidepdate >= ffromdate and a.applastemidepdate <= ftodate:
                                            a.delaydays1 = 0
                                            a.delaydays3 = 1
                                            a.flag = 'N'
                                        else:
                                            a.delaydays1 = 1
                                            a.delaydays3 = 2
                                            a.flag = 'Y'
                                    else:
                                        a.delaydays1 = 1
                                        a.flag = 'Y'
                                    
                                    if a.loantype == 'GROUP':
                                        if a.applastemidepdate >= ffromdategroup  and a.applastemidepdate <= ftodate:
                                            a.delaydays1 = 0
                                            a.delaydays3 = 1
                                            a.flag = 'N'
                                        else:
                                            a.delaydays1 = 1
                                            a.delaydays3 = 2
                                            a.flag = 'Y'
                                else:
                                    a.delaydays1 = 1
                                    a.delaydays3 = 2
                                    a.flag = 'Y'
                       
                                a.save()


                            collemidone = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A', delaydays1=0).values('locationcode','rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0))
                            colleminotdone = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A', delaydays1=1).values('locationcode','rpersoncode','rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0))

                            colldaywise = Loanmaster.objects.values('locationcode','rpersoncode','rpersonname','colldaynum','colldaychar').filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Sum('apploanemi')).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0)).order_by('colldaynum')
                            colltot = Loanmaster.objects.values('locationcode','rpersoncode','rpersonname').filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).annotate(okac=Count('loanid',filter=Q(delaydays3__in=[1]))).annotate(okamt=Coalesce(Sum('apploanemi',filter=Q(delaydays3__in=[1])),0)).annotate(notokac=Count('loanid',filter=~Q(delaydays3__in=[1]))).annotate(notokamt=Coalesce(Sum('apploanemi',filter=~Q(delaydays3__in=[1])),0))
                            
           
                            allemilist = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').order_by('colldaynum','id')
                    
                            frpersonname = allemilist[0].rpersonname
                            frpersoncode = allemilist[0].rpersoncode
                    
                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'frpersoncode':frpersoncode,
                                    'frpersonname':frpersonname,
                                    'allemilist':allemilist,
                                    'colldaywise' : colldaywise,
                                    'colltot' :colltot,
                                    }
                            return render(request, 'admssapp/emicollectorwisependinglistshow.html' , context)
        
                    return render(request, 'admssapp/emicollectorwisependinglist.html' , context)


###################################
######## EMI DAY WISE LIST ########
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emisummarywiselist(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    #ffromdate = loginrundate.strftime("%Y-%m-01")
                    #ftodate = loginrundate.strftime("%Y-%m-%d")
                    
                    all = Loanmaster.objects.filter(status="A")
                    for a in all:
                        a.delaydays1 = a.appemiduedate.weekday()
                        if a.applastemidepdate is not None:
                            delta = loginrundate - a.applastemidepdate
                        else:
                            delta = loginrundate - a.apploandate 
                    
                            a.delaydays2 = delta.days

                        a.delaydays3 =  (loginrundate - a.apploandate).days
                        a.save()

                        colldaywise = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname','colldaynum','colldaychar').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).order_by('colldaynum','rpersoncode')
                        colldaytot = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('locationcode','colldaynum','colldaychar').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0)).order_by('colldaynum')

                        colltot = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('apploanemi'),0))
                    
                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                'loginrundate':loginrundate,
                                'loginstatus':loginstatus,
                                'currdate':currdate,
                                'colldaywise':colldaywise,
                                'colldaytot':colldaytot,
                                'colltot':colltot,
                                    }
                        return render(request, 'admssapp/emidatewiselistshow.html' , context)



##################################
######## ASSOCIATE REPORT ########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def associatereport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")
                    asso = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(assoexp='Y')).values('associatecode', 'associatename').distinct().order_by('associatename')
                    assodatefrom = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(assoexp='Y')).order_by('apploandate').first()
                    assodateto = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(assoexp='Y')).order_by('apploandate').last()
                    ffromdate = assodatefrom.apploandate.strftime("%Y-%m-%d")
                    ftodate = assodateto.apploandate.strftime("%Y-%m-%d")

                    context={'loginlocationcode': loginlocationcode,
                            'loginlocationname': loginlocationname,
                            'loginrundate': loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'ffromdate': ffromdate,
                            'ftodate': ftodate,
                            'asso': asso,              
                             }

                    if request.method == "POST":
                            fassociatecode = request.POST.get('associate')
                            ffromdate = request.POST.get('fromdate')
                            ftodate = request.POST.get('todate')

                            assolist = Loanmaster.objects.filter(apploandate__range=(ffromdate, ftodate), locationcode=loginlocationcode, associatecode=fassociatecode).order_by('id')

                            fassociatecode = assolist[0].associatecode
                            fassociatename = assolist[0].associatename


                            #nac = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode, associatecode=fassociatecode).aggregate(total=Coalesce(Count('loanid'),0))
                            #namt = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode, associatecode=fassociatecode).aggregate(total=Coalesce(Sum('apploanamt'),0))
                            #nemi = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode, associatecode=fassociatecode).aggregate(total=Coalesce(Sum('apploanemi'),0))

                            #newloanac = nac.get("total")
                            #newloanamt = namt.get("total")
                            #newloanemi = nemi.get("total")

                            assolistssumm = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode, associatecode=fassociatecode).values('locationcode').annotate(total=Coalesce(Count('loanid'),0),apploanamt=Coalesce(Sum('apploanamt'),0),apploanemi=Coalesce(Sum('apploanemi'),0),assoexpamt=Coalesce(Sum('assoexpamt'),0))

                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'ffromdate' : ffromdate,
                                    'ftodate': ftodate,
                                    'assolist': assolist,
                                    'assolistssumm':assolistssumm,
                                    'fassociatecode': fassociatecode,
                                    'fassociatename': fassociatename,
                                      }
                            return render(request, 'admssapp/associatereportshow.html' , context)
        
                    return render(request, 'admssapp/associatereport.html' , context)



##########################################
######## ASSOCIATE PAYMENT REPORT ########
##########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def assoexppaymentreport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['B','A']): 
                  return HttpResponseRedirect('/login')
             else:


                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")
                    asso = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(assoexp='Y') & Q(assoexpstatus='Y')).values('associatecode', 'associatename').distinct().order_by('associatename')
                    assodatefrom = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A')).order_by('apploandate').first()
                    assodateto = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(assoexp='Y')).order_by('apploandate').last()

                    ffromdate = assodatefrom.apploandate.strftime("%Y-%m-%d")
                    ftodate = assodateto.apploandate.strftime("%Y-%m-%d")

                    context={'loginlocationcode': loginlocationcode,
                            'loginlocationname': loginlocationname,
                            'loginrundate': loginrundate,
                            'loginstatus':loginstatus,
                            'currdate': currdate,
                            'ffromdate': ffromdate,
                            'ftodate': ftodate,
                            'asso': asso,              
                             }

                    if request.method == "POST":
                            fassociatecode = request.POST.get('associate')
                            ffromdate = request.POST.get('fromdate')
                            ftodate = request.POST.get('todate')

                            assolist = Loanmaster.objects.filter(apploandate__range=(ffromdate, ftodate), locationcode=loginlocationcode, associatecode=fassociatecode, assoexpstatus="Y").order_by('id')

                            fassociatecode = assolist[0].associatecode
                            fassociatename = assolist[0].associatename
                           
                            assolistsumm = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode, associatecode=fassociatecode,assoexpstatus="Y").values('locationcode').annotate(total=Coalesce(Count('loanid'),0),apploanamt=Coalesce(Sum('apploanamt'),0),apploanemi=Coalesce(Sum('apploanemi'), 0),assoexpamt=Coalesce(Sum('assoexpamt'), 0))


                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'ffromdate' : ffromdate,
                                    'ftodate': ftodate,
                                    'assolist': assolist,
                                    'fassociatecode': fassociatecode,
                                    'fassociatename': fassociatename,
                                    'assolistsumm':assolistsumm,

                                     }
                            return render(request, 'admssapp/assoexppaymentreportshow.html', context)
        
                    return render(request, 'admssapp/assoexppaymentreport.html', context)

######################
#### MISC PAYMENT ####
######################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def miscpayment(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                if locationstatus=="A":
                    transnm = Transcd.objects.filter(Q(acperm = 'Y')  & Q(transtype='FD') & (~Q(advperm = 'Y'))).order_by('transnm')
                    transcd = Transcd.objects.filter(Q(acperm = 'Y')  & Q(transtype='FD') & (~Q(advperm = 'Y'))).order_by('transcd')
                else:
                    
                    transnm = Transcd.objects.filter((Q(acperm = 'Y') | Q(acperm = 'N'))  & Q(transtype='FD') & (~Q(advperm = 'Y'))).order_by('transnm')
                    transcd = Transcd.objects.filter((Q(acperm = 'Y') | Q(acperm = 'N'))  & Q(transtype='FD') & (~Q(advperm = 'Y'))).order_by('transcd')
                                                                                                                 

                allperson = Personmaster.objects.filter(locationcode=loginlocationcode).distinct('personname').order_by('personname')
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                clcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)[0].clcash
                clbank = allbank[0].clbank
                

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'transnm':transnm,
                        'transcd':transcd,
                        'allperson':allperson,
                        'allbank':allbank,
                        'clcash':clcash,
                        'clbank':clbank,
                        }

                
            
                if request.method == "POST":

                    ftranscd = request.POST.get('transcode')
                    eptranscd = Transcd.objects.get(transcd=ftranscd)
                    ftransnm = eptranscd.transnm
                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fpersoncode = request.POST.get('personname')
                    fremark = request.POST.get('remark').strip()


                    eptrans = Transcd.objects.get(transcd=ftranscd)
                    ftransnm = eptrans.transnm

                    eppersonmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)


                    fpersoncode = eppersonmast.personcode
                    fpersonname = eppersonmast.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash



                    if fmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        clbank = allbank.clbank

            
                    if fmode == "CASH" and fcashrec > clcash:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
        
                        success = True

                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        loguserid = request.session['loguserid']    
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

               
                        message="Not Sufficient Cash to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()


                        messages.success(request, message)
                        return HttpResponseRedirect('/miscpayment/')

                    if fmode == "BANK" and fcashrec > clbank:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
                        for all in allcash:
                            fclcash = all.clcash

                        success = True

                    
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

        
                        message="Not Sufficient Fund in Bank to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Bank Balance is Rs. "+str(clbank).strip()

                        messages.success(request, message)
                        return HttpResponseRedirect('/miscpayment/')


                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
                
                    fnarr = "Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                    if fremark == '':
                        fnarr = fnarr
                    else:
                        fnarr = fremark


                    if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id
                            
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - int(fcashrec)
                                all.save()
                            message="Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id
                            
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank - int(fcashrec)
                            allbank.save()

                            message="Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."


                    success = True
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status

                    allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)


                    messages.success(request, message)
                    return HttpResponseRedirect('/miscpayment/')
            
                else:
                    return render(request, 'admssapp/miscpayment.html' , context)


############################
#### MISC VOUCHAR PRINT ####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def miscvoucharprint(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
            
                ffromdate = ll.rundate
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          

                    dblist = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').order_by('id')


                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'dblist':dblist,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                        }
                
                    return render(request, 'admssapp/miscvoucharprintget.html' , context)
                else:
                    return render(request, 'admssapp/miscvoucharprint.html' , context)



@login_required(login_url='login')
@csrf_exempt
@never_cache
def miscvoucharprintshow(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
            
            
                if request.method == "POST":
                    fmiscvouchar = request.POST.get('miscvouchar')
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')
                                                 

                    dbvouc = Daybook.objects.get(locationcode=loginlocationcode,transid=fmiscvouchar,drcr='D')
        
                    inwords = num2words(dbvouc.amount)
                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'dbvouc':dbvouc,
                                    'inwords':inwords,
                            
                                    }
                
                    return render(request, 'admssapp/miscvoucharprintgetshow.html' , context)


#################################
#### ASSO EXP PAYMENT COMMIT ####
#################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def assoexppayment(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                allperson = Loanmaster.objects.filter(locationcode=loginlocationcode, assoexp='Y', assoexpstatus='N').values('associatecode','associatename').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('assoexpamt'),0)).order_by('associatename')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                        }

            
                if request.method == "POST":

                    fassociatecode = request.POST.get('assoperson_name')

                    assolist = Loanmaster.objects.filter(locationcode=loginlocationcode, assoexp='Y', assoexpstatus='N',associatecode=fassociatecode).values('associatecode','associatename','assoexpamt','loanid','apploandate','appname','apploanamt').order_by('id')
                    assosumm = Loanmaster.objects.filter(locationcode=loginlocationcode, assoexp='Y', assoexpstatus='N',associatecode=fassociatecode).values('associatecode','associatename').annotate(totac=Count('loanid')).annotate(totloanamt=Coalesce(Sum('apploanamt'),0)).annotate(totamt=Coalesce(Sum('assoexpamt'),0)).order_by('associatename')


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'assolist':assolist,
                            'assosumm':assosumm,
                            }

                    return render(request, 'admssapp/assoexppaymentlist.html' , context)
            
                else:
                    return render(request, 'admssapp/assoexppayment.html' , context)



##############################
#### ASSO EXP PAYMENT GET ####
##############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def assoexppaymentget(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
                                                                                                                

            
                if request.method == "POST":

                    fassociatecode = request.POST.get('assoperson_name')

                    assosumm = Loanmaster.objects.filter(locationcode=loginlocationcode, assoexp='Y', assoexpstatus='N',associatecode=fassociatecode).aggregate(totac=Coalesce(Count('loanid'),0),totamt=Coalesce(Sum('assoexpamt'),0))
                    assolist = Loanmaster.objects.filter(locationcode=loginlocationcode, assoexp='Y', assoexpstatus='N',associatecode=fassociatecode).values('associatecode','associatename','assoexpamt','loanid','appname','apploanamt').order_by('id')

                    fcashrec = assosumm.get("totamt")

                    allperson = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fassociatecode)

                    fpersoncode = allperson.personcode
                    fpersonname = allperson.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clbank = allbank[0].clbank
                    
                    ftranscd = '3361'
                    #'ASSOCIATE EXP'
                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftranscd = trans.transcd
                    ftransnm = trans.transnm
                    ftrans = trans.id

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'clcash':clcash,
                            'clbank':clbank,
                            'allbank': allbank,
                            'ftranscd':ftranscd,
                            'ftransnm':ftransnm,
                            'fpersoncode':fpersoncode,
                            'fpersonname':fpersonname,
                            'fcashrec':fcashrec,

                            }

                    return render(request, 'admssapp/assoexppaymentget.html' , context)
                else:
                    return render(request, 'admssapp/assoexppayment.html' , context)



#################################
#### ASSO EXP PAYMENT COMMIT ####
#################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def assoexppaymentcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

            
                if request.method == "POST":
                    fassociatecode = request.POST.get('assoperson_name')
                    ftranscd = request.POST.get('transcode')
                    eptrans = Transcd.objects.get(transcd=ftranscd)
                    ftransnm = eptrans.transnm

                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fpersoncode = request.POST.get('personname')
                    fremark = request.POST.get('remark')
                    
                    fbankac = ''

                    personmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)


                    fpersoncode = personmast.personcode
                    fpersonname = personmast.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash


                    if fmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        clbank = allbank.clbank

            
                    if fmode == "CASH" and fcashrec > clcash:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
        
                        success = True

                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        loguserid = request.session['loguserid']    
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status
                   
                
                        message="Not Sufficient Cash to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()


                        messages.success(request, message)
                        return HttpResponseRedirect('/assoexppayment/')

                    if fmode == "BANK" and fcashrec > clbank:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
                        for all in allcash:
                            fclcash = all.clcash

                        success = True

                    
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

                        message="Not Sufficient Fund in Bank to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Bank Balance is Rs. "+str(clbank).strip()

                        messages.success(request, message)
                        return HttpResponseRedirect('/assoexppayment/')


                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
           
                
                    fnarr = "Associate Exp Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                    if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - int(fcashrec)
                                all.save()
                    
                            message="Associate Exp Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id
                            
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank - int(fcashrec)
                            allbank.save()

                            message="Associate Exp Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                    
                    loanmaster = Loanmaster.objects.filter(locationcode=loginlocationcode,associatecode=fpersoncode,assoexpstatus='N')

                    for x in loanmaster:
                        x.assoexpstatus = 'Y'
                        x.assoexppaydate = loginrundate
                        x.assoexppaytransid = ftransid
                    
                        x.save()
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status

                    messages.success(request, message)
                    return HttpResponseRedirect('/assoexppayment/')
            
                else:
                    return render(request, 'admssapp/assoexppayment.html' , context)





#########################
#### ADVANCE PAYMENT ####
#########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def advancepayment(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                if locationstatus=="A":
                    transnm = Transcd.objects.filter(acperm="Y",transtype='FD').order_by('transnm')
                    transcd = Transcd.objects.filter(acperm="Y",transtype='FD').order_by('transcd')
                else:
                    transnm = Transcd.objects.filter(acperm__in=['Y','N'],advperm__in=['Y'],transtype='FD').order_by('transnm')
                    transcd = Transcd.objects.filter(acperm__in=['Y','N'],advperm__in=['Y'],transtype='FD').order_by('transcd')

                allperson = Personmaster.objects.filter(locationcode=loginlocationcode).distinct('personname').order_by('personname')
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'transnm':transnm,
                        'transcd':transcd,
                        'allperson':allperson,
                        'allbank':allbank,
                        }

               
            
                if request.method == "POST":

                    ftranscd = request.POST.get('transcode')
                    eptranscd = Transcd.objects.get(transcd=ftranscd)
                    ftransnm = eptranscd.transnm
                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fpersoncode = request.POST.get('personname')
                    fremark = request.POST.get('remark')
                    
                    fbankac = ''
                    fpersoncode = fpersoncode.split('.')[0]


                    eptrans = Transcd.objects.get(transcd=ftranscd)
                    ftransnm = eptrans.transnm

                    eppersonmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)


                    fpersoncode = eppersonmast.personcode
                    fpersonname = eppersonmast.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash


                    if fmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        clbank = allbank.clbank

            
                    if fmode == "CASH" and fcashrec > clcash:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
        
                        success = True

                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                        loguserid = request.session['loguserid']    
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status
                   
                
                        message="Not Sufficient Cash to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()


                        messages.success(request, message)
                        return HttpResponseRedirect('/advancepayment/')

                    if fmode == "BANK" and fcashrec > clbank:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
                        for all in allcash:
                            fclcash = all.clcash

                        success = True

                    
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

                        message="Not Sufficient Fund in Bank to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Bank Balance is Rs. "+str(clbank).strip()

                        messages.success(request, message)
                        return HttpResponseRedirect('/advancepayment/')


                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
           
                
                    fnarr = "Advance Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                    if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - int(fcashrec)
                                all.save()
                            message="Advance Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id

                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank - int(fcashrec)
                            allbank.save()

                            message="Advance Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                    adv = Advancesmaster(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,
                                         transid=ftransid,
                                         transcd=ftranscd,
                                         transnm=ftransnm,
                                         bankac=fbankac,
                                         chequeno=fappbankchq,
                                         mode=fmode,
                                         personcode=fpersoncode,
                                         personname=fpersonname,
                                         remark=fremark,
                                         dramount=fcashrec,
                                         balamount=fcashrec,
                                         status="A")
                    adv.save()
                    
                    
                    
                    success = True
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status

                    allperson = Personmaster.objects.filter(locationcode=loginlocationcode)
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)


                    messages.success(request, message)
                    return HttpResponseRedirect('/advancepayment/')
            
                else:
                    return render(request, 'admssapp/advancepayment.html' , context)



##################################
#### ADVANCE PAYMENT RECOVERY ####
##################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def advancepaymentcredit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                alladvance = Advancesmaster.objects.filter(locationcode=loginlocationcode,status='A')
                alltotal = Advancesmaster.objects.filter(locationcode=loginlocationcode).values('locationcode','locationname').aggregate(totalac=Coalesce(Count('transid'),0),drtotal=Coalesce(Sum('dramount'), 0),crtotal=Coalesce(Sum('cramount'),0))

     
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'alladvance':alladvance,
                        'alltotal':alltotal
                           }

                return render(request, 'admssapp/advancepaymentscredit.html' , context)




##########################################
#### ADVANCE PAYMENT RECOVERY LIST    ####
##########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def advancepaymentcreditlist(request,advanceid):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                alladvance = Advancesmaster.objects.get(locationcode=loginlocationcode,id=advanceid)
                
                fpersoncode = alladvance.personcode 
                fpersonname = alladvance.personname 
                ftransnm =  alladvance.transnm 
                fdramount = alladvance.dramount
                fcramount = alladvance.cramount
                fbalamount = alladvance.balamount
                fadvdate =  alladvance.date
                ftransid = alladvance.transid
  
 
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'fpersoncode':fpersoncode,
                        'fpersonname':fpersonname,
                        'ftransnm': ftransnm,
                        'fdramount': fdramount,
                        'fcramount' : fcramount,
                        'fbalamount': fbalamount,
                        'fadvdate': fadvdate,
                        'ftransid':ftransid,
                        'allbank':allbank,
                         }
            
                return render(request, 'admssapp/advancepaymentcreditcommit.html' , context)



##########################################
#### ADVANCE PAYMENT RECOVERY COMMIT  ####
##########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def advancepaymentcreditcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:



                if request.method == "POST":

                    fadvid = request.POST.get('transid')

                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fbankac = ''


                    alladv = Advancesmaster.objects.get(locationcode=loginlocationcode,transid=fadvid)
                
                    ftransnm = alladv.transnm
                    
                    ftranscd = alladv.transcd
                    
                    fpersoncode = alladv.personcode
                    
                    fpersonname = alladv.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash
    

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
           
                
                    fnarr = "Advance Payment Recovery/"+ftransnm.strip()+"/"+fpersonname.strip()
                    if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="C",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash + int(fcashrec)
                                all.save()
                            message="Advance Payment Recovery of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="C",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="D",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            message="Advance Payment Recovery of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                    adv = Advancestrans(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,
                                         advanceid = alladv.transid,
                                         transid=ftransid,
                                         transcd=ftranscd,
                                         transnm=ftransnm,
                                         bankac=fbankac,
                                         chequeno=fappbankchq,
                                         mode=fmode,
                                         personcode=fpersoncode,
                                         personname=fpersonname,
                                         amount=fcashrec,
                                         drcr="C",
                                         master_id = alladv.id)
                    adv.save()
                    
                    alladv.cramount = alladv.cramount + fcashrec
                    alladv.balamount = alladv.balamount - fcashrec
                    
                    if alladv.dramount == alladv.cramount:
                        alladv.status = 'C'
                    
                    alladv.save()
                    
                    success = True
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status

                    messages.success(request, message)
                    return HttpResponseRedirect('/advancepaymentcredit/')





##########################################
#### AUTHORISE CENTER EXPENSE PAYMENT ####
##########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def authcenterexpensepayment(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['A']):
                return HttpResponseRedirect('/login')
         else:


                ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,paid='N',amount__gt=0)
                ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode,paid='N',amount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('amount'), 0))

                famount = ispaidsumm.get("amt")

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ispaid':ispaid,
                        'ispaidsumm':ispaidsumm,
                        'famount':famount,
                          }

            
                if request.method == "POST":

                    ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,paid='N',amount__gt=0)
                    ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode,paid='N',amount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('amount'), 0))
                    famount = ispaidsumm.get("amt")

                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    fpersoncode = ispaid[0].personcode
                    fpersonname = ispaid[0].personname



                    context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'famount':famount,
                        'allbank':allbank,
                        'fpersoncode':fpersoncode,
                        'fpersonname':fpersonname,
                          }

                    return render(request, 'admssapp/authcenterexpensecommit.html', context)
                else:
                    return render(request, 'admssapp/authcenterexpense.html' , context)




#################################################
#### AUTHORISE CENTER EXPENSE PAYMENT COMMIT ####
#################################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def authcenterexpensepaymentcommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['A']):
                return HttpResponseRedirect('/login')
         else:


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                          }
            
                if request.method == "POST":

                    fmode = request.POST.get('mode').upper()
                    fappbankac = request.POST.get('bankac')
                    fappbankchq = request.POST.get('bankchq')


                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash

                    ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode, paid='N', amount__gt=0)
                    ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode, paid='N', amount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('amount'), 0))
                    netamt = ispaidsumm.get("amt")

                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode, date=loginrundate)
                    fpersoncode = ispaid[0].personcode
                    fpersonname = ispaid[0].personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname


 

                    if fmode == "BANK":
                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        clbank = allbank.clbank
                        if clbank < netamt:
                            message = "Not Sufficient Bank Balance for Payment of "+fexpensetypename.strip() + " Rs. "+str(netamt).strip()+" Bank is Rs. "+str(clbank).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/authcenterexpensepayment/')
                        

            
                    if fmode == "CASH":

                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)[0]
                        clcash = allcash.clcash
                        if clcash < netamt:
                            message="Not Sufficient Cash Balance for Payment of "+fexpensetypename.strip()+" Rs. "+str(netamt).strip()+" Cash is Rs. "+str(clcash).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/authcenterexpensepayment/')



                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
           
                

                    if fmode == "CASH":

                            for x in ispaid:
                           
                                trans = Transcd.objects.get(transcd=x.transcd)
                                ftrans = trans.id
                                ftranscd = trans.transcd
                                ftransnm = trans.transnm
                                famount = x.amount

                            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id
                                
                                fnarr = "Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                                
                                db = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,transid=ftransid,
                                        transcd=ftranscd,transnm=ftransnm,
                                        bankac=fappbankac,
                                        mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                             narration=fnarr, amount=famount, drcr="D", trans_id=ftrans,
                                        clcashbank_id = opclid)
                                db.save()
            
                                x.date = loginrundate
                                x.transid = ftransid
                                x.mode = fmode
                                x.paid = 'Y'
                                x.save()


                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - int(netamt)
                                all.save()
                            message = "Payment of "+ftransnm.strip()+" Rs. "+str(netamt).strip()+" for " + fpersonname.strip()+" Processed successfully by Cash..."



                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            for x in ispaid:
                           
                                trans = Transcd.objects.get(transcd=x.transcd)
                                ftrans = trans.id
                                ftranscd = trans.transcd
                                ftransnm = trans.transnm
                                famount = x.amount                            

                            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,transid=ftransid,
                                        transcd=ftranscd,transnm=ftransnm,
                                        bankac=fbankac,
                                        chequeno=fappbankchq,
                                        mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                             narration=fnarr, amount=famount, drcr="D", trans_id=ftrans,
                                        clcashbank_id = opclid)
            
                                db.save()

                                x.date = loginrundate
                                x.transid = ftransid
                                x.mode = fmode
                                x.paid = 'Y'
                                x.save()

                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                                
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(netamt),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank - int(netamt)
                            allbank.save()

                            message="Payment of "+ftransnm.strip()+" Rs. "+str(netamt).strip()+" for "+fpersonname.strip()+" Processed successfully by Bank..."


                    

            

                    success = True
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status


                    messages.success(request, message)
                    return HttpResponseRedirect('/authcenterexpensepayment/')
            
                else:
                    return render(request, 'admssapp/authcenterexpense.html', context)





#################################
###### MISC PAYMENT REPORT ######
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def miscpaymentreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                ffromdate = ll.rundate
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')    
                    
                    fffromdate = ffromdate      
                    fftodate = ftodate      

                    db = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').aggregate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))
                    #dblist = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').values('transcd','transnm').annotate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))
                    dblist = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').order_by('id')
                    dbsumm = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').values('drcr').annotate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))
                    totalentry =  db.get("totalac")
                    totalamount =  db.get("totalamt")

                
                    fddmmyyyy = fffromdate[8:10:1] + "-" + fffromdate[5:7:1] + "-" + fffromdate[0:4:1]
                    tddmmyyyy = fftodate[8:10:1] + "-" + fftodate[5:7:1] + "-" + fftodate[0:4:1]
                    

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'fddmmyyyy':fddmmyyyy,
                            'tddmmyyyy':tddmmyyyy,
                            'dblist':dblist,
                            'dbsumm':dbsumm,
                            'totalentry':totalentry,
                            'totalamount':totalamount,
                                        }
                
                    return render(request, 'admssapp/miscpaymentreportshow.html', context)
                else:
                    return render(request, 'admssapp/miscpaymentreport.html', context)



##################################
###### MISC PAYMENT SUMMARY ######
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def miscsummaryreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()


         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
            
                ffromdate = ll.rundate
                ftodate = ll.rundate

            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')    

                    
                    fffromdate = ffromdate      
                    fftodate = ftodate      


                    db = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').aggregate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))

                    dbsumm = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').values('drcr').annotate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0))
                    dblist = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,trans__transtype="FD",drcr='D').values('transcd','transnm','drcr').annotate(totalac=Coalesce(Count('transcd'),0),totalamt=Coalesce(Sum('amount'),0)).order_by('transnm')

                    totalentry =  db.get("totalac")
                    totalamount =  db.get("totalamt")

                
                    fddmmyyyy = fffromdate[8:10:1] + "-" + fffromdate[5:7:1] + "-" + fffromdate[0:4:1]
                    tddmmyyyy = fftodate[8:10:1] + "-" + fftodate[5:7:1] + "-" + fftodate[0:4:1]
                    

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'fddmmyyyy':fddmmyyyy,
                            'tddmmyyyy':tddmmyyyy,
                            'dblist':dblist,
                            'dbsumm':dbsumm,
                            'totalentry':totalentry,
                            'totalamount':totalamount,
                                        }
                
                    return render(request, 'admssapp/miscsummaryreportshow.html', context)
                else:
                    return render(request, 'admssapp/miscsummaryreport.html', context)


##########################
#### BANK TRANSACTION ####
##########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def banktrans(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('-opbank')
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('-opbank')
                allperson = Personmaster.objects.filter(locationcode=loginlocationcode).distinct().order_by('personname')           
            
                fclcash = allcash[0].clcash
        

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'allperson':allperson,
                        }
        
            
                if request.method == "POST":
                    ftranstype = request.POST.get('transtype').upper()
                    fappbankac = request.POST.get('appbankac')
                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode')
                    fappbankchq = request.POST.get('appbankchq')
                    fpersoncode = request.POST.get('personname')

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    ftranscd = allbank.bankcode
                    ftransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fmode = 'BANK'

                    eppersonmast = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)

                    fpersoncode = eppersonmast.personcode
                    fpersonname = eppersonmast.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    allcash = Opclcashbank.objects.filter(
                        locationcode=loginlocationcode, date=loginrundate).order_by('bankac')
                    clcash = allcash[0].clcash

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    clbank = allbank.clbank




                    if ftranstype == "DEPOSIT" and fcashrec > clcash:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     

                        success = True

                        fclcash = allcash[0]
        
                        message="Not Sufficient Fund in Cash to Deposit in Bank. Deposit Amount Rs. "+str(fcashrec).strip()+" but Cash Balance is Rs. "+str(clcash).strip()

                        messages.success(request, message)
                        return HttpResponseRedirect('/banktrans/')



        
                    if ftranstype == "WITHDRAWL" and fcashrec > clbank:

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     

                        success = True

                        fclcash = allcash[0]
                    
                        message="Not Sufficient Fund in Bank a/c "+fbankac+"to Withdrawl. Withdrawl Amount Rs. "+str(fcashrec).strip()+" but Bank Balance is Rs. "+str(clbank).strip()

                        messages.success(request, message)
                        return HttpResponseRedirect('/banktrans/')

                


                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()


                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftrans = trans.id
                
                    if ftranstype == "DEPOSIT":
                        fnarr = "Cash Deposit / "+fbankacname

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        opclid = allbank.id
                                            
                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftranscd,transnm=ftransnm,
                            bankac=fbankac,
                            loanid = fbankac,
                            mode=fmode,chequeno=fappbankchq,
                            narration=fnarr,amount=fcashrec,
                            personcode=fpersoncode,personname=fpersonname,
                            drcr="D", trans_id = ftrans,
                            clcashbank_id = opclid)

                        db.save()
                        fmessage="Cash Deposit in Bank Rs."+str(fcashrec).strip()+" by "+fpersonname.strip()+" is Successfuly updated..."
                    
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        for all1 in allcash:
                            all1.clcash = all1.clcash - int(fcashrec)
                            all1.save()

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank = allbank.clbank + int(fcashrec)
                        allbank.save()

                        

                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftrans = trans.id

                    if ftranstype == "WITHDRAWL":
                        fnarr = "Cash Withdrawl / "+fbankacname

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        opclid = allbank.id

                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftranscd,transnm=ftransnm,
                            mode=fmode,chequeno=fappbankchq,
                            bankac=fbankac,
                            loanid = fbankac,
                            narration=fnarr,amount=fcashrec,
                            personcode=fpersoncode,personname=fpersonname,
                            drcr="C",trans_id = ftrans,
                            clcashbank_id = opclid)

                        db.save()
                        fmessage="Cash Withdrawl from Bank Rs. "+str(fcashrec).strip()+" by "+fpersonname.strip()+" is Successfuly updated..."
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                        for all1 in allcash:
                            all1.clcash = all1.clcash + int(fcashrec)
                            all1.save()

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank = allbank.clbank - int(fcashrec)
                        allbank.save()

                    success = True

                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                
                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                    allperson = Personmaster.objects.filter(locationcode=loginlocationcode)     
                    
                    fclcash = allcash[0].clcash
        
                    message = ftranstype+" / "+fbankac+" / "+fbankacname+" /Rs. "+str(fcashrec)+" / "+"Processed Succesfully"

                    messages.success(request, message)
                    return HttpResponseRedirect('/banktrans/')

                else:

                    return render(request, 'admssapp/banktrans.html' , context)


##############################
#### BANK TRANSFER TO A/C ####
##############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def banktransac(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
        
        

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        }
        
            
                if request.method == "POST":
                    ffrombankac = request.POST.get('frombankac')


                    frombank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ffrombankac,date=loginrundate)

                    ffromtranscd = frombank.bankcode
                    ffromtransnm = frombank.bankname
                    ffrombankac = frombank.bankac
                    ffrombankacname = frombank.bankacname
                    ffrombankclbank = frombank.clbank



                    tobank = Opclcashbank.objects.filter(Q(locationcode=loginlocationcode) & Q(date=loginrundate) & ~Q(bankac=ffrombankac))

                    context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'frombank':frombank,
                        'ffrombankac':ffrombankac,
                        'ffrombankacname':ffrombankacname,
                        'ffrombankclbank':ffrombankclbank,
                        'tobank':tobank,
                        }
        


                    return render(request, 'admssapp/banktransacget.html' , context)

                else:

                    return render(request, 'admssapp/banktransac.html' , context)



#####################################
#### BANK TRANSFER TO A/C COMMIT ####
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def banktransaccommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         

                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        }
        
            
                if request.method == "POST":
                    ffrombankac = request.POST.get('frombankac')
                    ftobankac = request.POST.get('tobankac')
                    fbankchq = request.POST.get('bankchq')
                    famount = request.POST.get('amount')


                    frombank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ffrombankac,date=loginrundate)
                    tobank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ftobankac,date=loginrundate)

                    ffromtranscd = frombank.bankcode
                    ffromtransnm = frombank.bankname
                    ffrombankac = frombank.bankac
                    ffrombankacname = frombank.bankacname
                    ffrombankclbank = frombank.clbank


                    ftotranscd = tobank.bankcode
                    ftotransnm = tobank.bankname
                    ftobankac = tobank.bankac
                    ftobankacname = tobank.bankacname
                    ftobankclbank = tobank.clbank


                    if ffrombankclbank < int(famount):
                            message = "Not sufficient Bank Balance  / " + ffrombankac+" / "+ ffrombankclbank +" to transfer in  "+ftobankac + "..."

                            messages.success(request, message)
                            return HttpResponseRedirect('/banktransac/')



                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()


                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                   
                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)  

                    frombank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ffrombankac,date=loginrundate)
                    opclid = frombank.id
                    
                    trans = Transcd.objects.get(transcd=ffromtranscd)
                    ftrans = trans.id

                    fmode = 'BANK'

                    fnarr = 'Fund Transfer from Bank a/c ' +  ffrombankac + ' to bank a/c ' + ftobankac
                                            
                    db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ffromtranscd,transnm=ffromtransnm,
                            bankac=ffrombankac,
                            loanid = ffrombankac,
                            mode=fmode,chequeno=fbankchq,
                            narration=fnarr,amount=famount,
                            drcr="C", trans_id = ftrans,
                            clcashbank_id = opclid)
                    db.save()


                    tobank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ftobankac,date=loginrundate)
                    opclid = frombank.id
                    
                    trans = Transcd.objects.get(transcd=ftotranscd)
                    ftrans = trans.id

                    fmode = 'BANK'

                    fnarr = 'Fund Transfer from Bank a/c ' +  ffrombankac + 'to bank a/c ' + ftobankac
                                            
                    db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftotranscd,transnm=ftotransnm,
                            bankac=ftobankac,
                            loanid = ftobankac,
                            mode=fmode,chequeno=fbankchq,
                            narration=fnarr,amount=famount,
                            drcr="D", trans_id = ftrans,
                            clcashbank_id = opclid)
                    db.save()
                    


                    frombank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ffrombankac,date=loginrundate)
                    frombank.clbank = frombank.clbank - int(famount)
                    frombank.save()

                    tobank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=ftobankac,date=loginrundate)
                    tobank.clbank = tobank.clbank + int(famount)
                    tobank.save()

                    success = True

                    message = "Fund Transferred from Bank a/c " + ffrombankac+" / "+ str(famount) +" to Bank a/c  "+ftobankac + " through "+fbankchq + " Successfully..."

                    messages.success(request, message)
                    return HttpResponseRedirect('/banktransac/')





#################################
#### BANK TRANSACTION REPORT ####
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def banktransreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
            
                ffromdate = ll.rundate
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    fappbankac = request.POST.get('appbankac')
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          


                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    ftranscd = allbank.bankcode
                    ftransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fmode = 'BANK'
                    
                    ## UPDATE CLBANK ##
                    #cl = Daybook.objects.all()
                    #for c in cl:
                    #    dt = c.date
                    #    fbankac = c.bankac
                    #    opcl1 = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=dt,bankac='3210214000012').first()
                    #    iid = opcl1.id
                    #    opcl = Opclcashbank.objects.get(id=iid)
                    #    rec = opcl.id
                    #    c.clcashbank_id = rec
                    #    c.save()
                        

                    dbbank = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=fappbankac,transcd=allbank.bankcode).select_related('clcashbank').order_by('date','id')

                    

                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'fbankac':fbankac,
                                    'dbbank':dbbank,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                        }
                
                    return render(request, 'admssapp/banktransreportshow.html', context)
                else:
                    return render(request, 'admssapp/banktransreport.html', context)



############################
#### BANK VOUCHAR PRINT ####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def bankvoucharprint(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
            
                ffromdate = ll.rundate
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    ftranstype = request.POST.get('transtype').upper()
                    fappbankac = request.POST.get('appbankac')
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          


                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    ftranscd = allbank.bankcode
                    ftransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fmode = 'BANK'


                    if ftranstype == "DEPOSIT":

                        dbbank = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=fappbankac,drcr='D',transcd=allbank.bankcode).order_by('date')



        
                    if ftranstype == "WITHDRAWL":

                        dbbank = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,bankac=fappbankac,drcr='C',transcd=allbank.bankcode).order_by('date')

        
                    

                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'ftranstype':ftranstype,
                                    'fbankac':fbankac,
                                    'dbbank':dbbank,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                        }
                
                    return render(request, 'admssapp/bankvoucharprintget.html' , context)
                else:
                    return render(request, 'admssapp/bankvoucharprint.html' , context)



@login_required(login_url='login')
@csrf_exempt
@never_cache
def bankvoucharprintshow(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
            
            
                if request.method == "POST":
                    ftranstype = request.POST.get('transtype').upper()
                    fappbankac = request.POST.get('appbankac')
                    fbankvouchar = request.POST.get('bankvouchar')
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          


                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    ftranscd = allbank.bankcode
                    ftransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fmode = 'BANK'


                    if ftranstype == "DEPOSIT":

                        dbbank = Daybook.objects.get(locationcode=loginlocationcode,transid=fbankvouchar,bankac=fappbankac,drcr='D',transcd=allbank.bankcode)

        
                    if ftranstype == "WITHDRAWL":

                        dbbank = Daybook.objects.get(locationcode=loginlocationcode,transid=fbankvouchar,bankac=fappbankac,drcr='C',transcd=allbank.bankcode)

        
                    inwords = num2words(dbbank.amount)
                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'ftranstype':ftranstype,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'fbankac':fbankac,
                                    'dbbank':dbbank,
                                    'allbank':allbank,
                                    'inwords':inwords,
                            
                                    }
                
                    return render(request, 'admssapp/bankvoucharprintgetshow.html' , context)
  



##########################
##### BANK CHARGES  ######
##########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def bankcharges(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                bankcharge = Transcd.objects.filter(transtype='BC')
                    
                for all in allcash:
                    fclcash = all.clcash


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'bankcharge':bankcharge,
                        }
        
            
                if request.method == "POST":
                    fappbankac = request.POST.get('appbankac')
                    fcashrec = int(request.POST.get('cashrec'))
                    fbankchargecode = request.POST.get('bankchargecode')
                    fmode = request.POST.get('emimode')
        

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    fbanktranscd = allbank.bankcode
                    fbanktransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fclbank = allbank.clbank
                    fmode = 'BANK'

                    if fclbank >= fcashrec:

                    
                        transcd = Transcd.objects.get(transcd=fbankchargecode)
                        ftranscd = transcd.transcd
                        ftransnm = transcd.transnm

                        fpersoncode = ""
                        fpersonname = ""

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname



                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()



                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    

                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)        

                        trans = Transcd.objects.get(transcd=ftranscd)
                        ftrans = trans.id    
        
                        fnarr = "Bank Charges / "+fbankacname

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        opclid = allbank.id

                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftranscd,transnm=ftransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="D",trans_id = ftrans,
                            clcashbank_id = opclid)
                        db.save()


                        trans = Transcd.objects.get(transcd=fbanktranscd)
                        ftrans = trans.id    
                        
        
                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=fbanktranscd,transnm=fbanktransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="C",trans_id = ftrans,
                            clcashbank_id = opclid)
                        db.save()
                    

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank = allbank.clbank - int(fcashrec)
                        allbank.save()
                    
                        success = True
                        ftranstype = fnarr

                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        bankcharge = Transcd.objects.filter(transtype='BC')
                    

                        for all in allcash:
                            fclcash = all.clcash

                        ftranstype = fnarr

                        message = ftranstype+" / "+fbankac+" / "+fbanktransnm+" /Rs. "+str(fcashrec)+" / "+"Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/bankcharges/')

                    else:
                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).order_by('bankac')
                        bankcharge = Transcd.objects.filter(transtype='BC')
                    
                        for all in allcash:
                            fclcash = all.clcash

            
                        message = "Not Sufficient Balance in Bank a/c " + fbankac + " to Adjust Bank Charges."+"Bank Charges Rs."+str(fcashrec)+" Bank Balance Rs."+str(fclbank)

                        messages.success(request, message)
                        return HttpResponseRedirect('/bankcharges/')

                else:
                    return render(request, 'admssapp/bankcharges.html' , context)




##########################
##### BANK INTREST  ######
##########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def bankintrest(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                bankintrest = Transcd.objects.filter(transtype='BI')
                    
                for all in allcash:
                    fclcash = all.clcash


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'bankintrest':bankintrest,
                        }
        
            
                if request.method == "POST":
                    fappbankac = request.POST.get('appbankac')
                    fcashrec = int(request.POST.get('cashrec'))
                    fbankintrestcode = request.POST.get('bankintrestcode')
                    fmode = request.POST.get('emimode')
            

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    fbanktranscd = allbank.bankcode
                    fbanktransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fmode = 'BANK'
                    
                    fbankintrestcode='3350'
                    transcd = Transcd.objects.get(transcd=fbankintrestcode)
                    ftranscd = transcd.transcd
                    ftransnm = transcd.transnm


                    fpersoncode = ""
                    fpersonname = ""

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname


                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()


                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            


                    trans = Transcd.objects.get(transcd=ftranscd)
                    ftrans = trans.id    
                                    

                    fnarr = "Bank Intrest / "+fbankacname

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                    opclid = allbank.id

                    db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftranscd,transnm=ftransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="C", trans_id = ftrans,
                            clcashbank_id = opclid
                             )
                    db.save()

                    trans = Transcd.objects.get(transcd=fbanktranscd)
                    ftrans = trans.id    
                                    

                    db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=fbanktranscd,transnm=fbanktransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="D",trans_id = ftrans,
                            clcashbank_id = opclid
                             )
                    db.save()
                    

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    allbank.clbank = allbank.clbank + int(fcashrec)
                    allbank.save()


                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    bankintrest = Transcd.objects.filter(transtype='BI')
                    
                    for all in allcash:
                        fclcash = all.clcash
                                
                    ftranstype = fnarr
        
                    message = ftranstype+" / "+fbankac+" / "+fbanktransnm+" /Rs. "+str(fcashrec)+" / "+"Processed Succesfully"
            
                    messages.success(request, message)
                    return HttpResponseRedirect('/bankintrest/')

                else:
                    return render(request, 'admssapp/bankintrest.html' , context)



##########################
##### BANK DISHONOR ######
##########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def bankdishonor(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                bankdishonor = Transcd.objects.filter(transcd='3357', transtype='BC')
                    
                
                fclcash = allcash[0] 


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'bankdishonor': bankdishonor,
                        }
        
            
                if request.method == "POST":
                    fappbankac = request.POST.get('appbankac')
                    fcashrec = int(request.POST.get('cashrec'))
                    fbankchargecode = request.POST.get('bankchargecode')
                    fmode = request.POST.get('emimode')
        

                    allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                    fbanktranscd = allbank.bankcode
                    fbanktransnm = allbank.bankname
                    fbankac = allbank.bankac
                    fbankacname = allbank.bankacname
                    fclbank = allbank.clbank
                    fmode = 'BANK'

                    if fclbank >= fcashrec:

                    
                        transcd = Transcd.objects.get(transcd=fbankchargecode)
                        ftranscd = transcd.transcd
                        ftransnm = transcd.transnm

                        fpersoncode = ""
                        fpersonname = ""

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname



                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()



                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    

                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)        

                        trans = Transcd.objects.get(transcd=ftranscd)
                        ftrans = trans.id    
        
                        fnarr = "Bank Charges / "+fbankacname

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                        opclid = allbank.id

                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=ftranscd,transnm=ftransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="D",trans_id = ftrans,
                            clcashbank_id = opclid)
                        db.save()


                        trans = Transcd.objects.get(transcd=fbanktranscd)
                        ftrans = trans.id    
                        
        
                        db = Daybook(locationcode=loginlocationcode,
                            locationname=loginlocationname,
                            date=loginrundate,transid=ftransid,
                            transcd=fbanktranscd,transnm=fbanktransnm,
                            bankac=fbankac,
                            mode=fmode,
                            narration=fnarr,amount=fcashrec,
                            drcr="C",trans_id = ftrans,
                            clcashbank_id = opclid)
                        db.save()
                    

                        allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                        allbank.clbank = allbank.clbank - int(fcashrec)
                        allbank.save()
                    
                        success = True
                        ftranstype = fnarr



                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        currdate = date.today()
                
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        bankcharge = Transcd.objects.filter(transtype='BC')
                    
                        for all in allcash:
                            fclcash = all.clcash



                        context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'success':True,
                                    'ftranstype':fnarr,
                                    'ftransnm':ftransnm,
                                    'fbankac':fbankac,
                                    'fbanktransnm':fbanktransnm,
                                    'ftransnm':ftransnm,
                                    'allbank':allbank,
                                    'fclcash':fclcash,
                                    'bankcharge':bankcharge,
                                    'fcashrec':fcashrec,
                                    }
                
        
                        messages.success(request, message)
                        return HttpResponseRedirect('/bankdishonor/')


                    else:
                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        bankcharge = Transcd.objects.filter(transtype='BC')
                    
                        for all in allcash:
                            fclcash = all.clcash

                        message = "Not Sufficient Balance in Bank to Adjust Bank Charges"

                        messages.success(request, message)
                        return HttpResponseRedirect('/bankdishonor/')

                else:
                    return render(request, 'admssapp/bankdishonor.html', context)






######################
####### FUND IN ######
######################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundin(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                if loginstatus == 'A':
                    fundcode = Transcd.objects.filter(transtype='FC',acperm='Y')    
                elif loginstatus == 'B':    
                    fundcode = Transcd.objects.filter(transtype='FC')
                    
                allperson = Personmaster.objects.filter(locationcode=loginlocationcode,persontype__in=['DIR','ACH','INV','ACP','EMP']).order_by('personname')

                for all in allcash:
                    fclcash = all.clcash


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'fundcode':fundcode,
                        'allperson':allperson,
                        }

                if request.method == "POST" and request.POST.get('checkbox') is not None:

                        ffundcode = request.POST.get('fundcode')
                        fpersoncode = request.POST.get('personcode')
                        frelatedpersonname = request.POST.get('relatedperson')
                        fappbankac = request.POST.get('appbankac')
                        ftranstype = request.POST.get('transtype').upper()
                        fpaymode = request.POST.get('paymode').upper()
                        fappbankchq = request.POST.get('appbankchq')
                        fcashrec = request.POST.get('cashrec')
                        fcheckbox = request.POST.get('checkbox')
                        fintrestmode = request.POST.get('intrestmode')

                        fmis = 'N'
                        fmisamount = 0
                        finttype = 'YEARLY'
                        fintduedate = None


                        if fintrestmode == 'MONTHLY':
                            fmis = 'Y'
                            fmisamount = fcashrec
                            finttype = 'MONTHLY'
                            fintduedate = loginrundate +  relativedelta(months=+1)
                        

                        fclbank = 0
                        fbankac = "                "
                        fclcash = 0
                        
                    
                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        trans = Transcd.objects.get(transcd=ffundcode)
                        ftranscd = trans.transcd
                        ftransnm = trans.transnm

                        person = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)
                        fpersoncode=person.personcode
                        fpersonname=person.personname
                        fpersondesig = person.persondesig
                        fpersontype = person.persontype
                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                        fdrcr = "C"
                        fnarr = "FUND IN/"+ftransnm.strip()+"/"+fpersonname.strip()
                        fnarr1 = "FUND IN / "+ftransnm.strip()+" / "+fpersonname.strip()
        

                        if fpaymode=="BANK":
                            
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname


                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id
                            

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id    

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=fbankcode,transnm=fbankname,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="D", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            allbank.clbank = allbank.clbank + int(fcashrec)
                            allbank.save()



                        if fpaymode=="CASH":

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    
                            for all in allcash:
                                fclcash = all.clcash
                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()
            
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash + int(fcashrec)
                                all.save()

            
                            
                        fm = Fundmaster(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date = loginrundate,transid = ftransid,
                                    transcd = ftranscd,transnm = ftransnm,
                                    bankac = fbankac,
                                    mode = fpaymode,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    relatedpersonname = frelatedpersonname,
                                    persondesig = fpersondesig,
                                    persontype = fpersontype,
                                    amount = fcashrec,
                                    status = 'A',
                                    misamount = fcashrec,
                                    mis=fmis,
                                    intduedate = fintduedate,
                                    intrate='1.00',
                                    inttype=fintrestmode,
                                    drcr = fdrcr)

                        fm.save()
                        ftranstype = fnarr1
                        
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        fundcode = Transcd.objects.filter(transtype='FC')
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode,persontype__in=['DIR','ACH','INV'])

                        for all in allcash:
                            fclcash = all.clcash     

                        message = ftranstype+" / "+ fpaymode+" / "+fbankac+" /Rs. "+fcashrec+" / "+"Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundin/')
                    
                else:
                        return render(request, 'admssapp/fundin.html' , context)



##########################
####### FUND IN OTH ######
##########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundinoth(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                if loginstatus == 'A':
                    fundcode = Transcd.objects.filter(transtype='FCOTH')    
                elif loginstatus == 'B':    
                    fundcode = Transcd.objects.filter(transtype='FCOTH')
                    
                allperson = Personmaster.objects.filter(locationcode=loginlocationcode,persontype__in=['COLL','DIR','ACH','INV','ACP','EMP']).order_by('personname')

                for all in allcash:
                    fclcash = all.clcash


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'fundcode':fundcode,
                        'allperson':allperson,
                        }

                if request.method == "POST" and request.POST.get('checkbox') is not None:

                        ffundcode = request.POST.get('fundcode')
                        fpersoncode = request.POST.get('personcode')
                        fappbankac = request.POST.get('appbankac')
                        ftranstype = request.POST.get('transtype').upper()
                        fpaymode = request.POST.get('paymode').upper()
                        fappbankchq = request.POST.get('appbankchq')
                        fcashrec = request.POST.get('cashrec')
                        fcheckbox = request.POST.get('checkbox')


                        fclbank = 0
                        fbankac = "                "
                        fclcash = 0
                        
                    
                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        trans = Transcd.objects.get(transcd=ffundcode)
                        ftranscd = trans.transcd
                        ftransnm = trans.transnm

                        person = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)
                        fpersoncode=person.personcode
                        fpersonname=person.personname
                        fpersondesig = person.persondesig
                        fpersontype = person.persontype
                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                        fdrcr = "C"
                        fnarr = "FUND IN OTH/"+ftransnm.strip()+"/"+fpersonname.strip()
                        fnarr1 = "FUND IN OTH/ "+ftransnm.strip()+" / "+fpersonname.strip()
        

                        if fpaymode=="BANK":
                            
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname


                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id
                            

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id    

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=fbankcode,transnm=fbankname,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="D", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            allbank.clbank = allbank.clbank + int(fcashrec)
                            allbank.save()



                        if fpaymode=="CASH":

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    
                            for all in allcash:
                                fclcash = all.clcash
                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()
            
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash + int(fcashrec)
                                all.save()

            

                        fm = Fundmasteroth(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date = loginrundate,transid = ftransid,
                                    transcd = ftranscd,transnm = ftransnm,
                                    bankac = fbankac,
                                    mode = fpaymode,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    persondesig = fpersondesig,
                                    persontype = fpersontype,
                                    amount = fcashrec,
                                    status = 'A',
                                    drcr = fdrcr)

                        fm.save()
                        ftranstype = fnarr1
                        
                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        fundcode = Transcd.objects.filter(transtype='FC')
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode,persontype__in=['DIR','ACH','INV'])

                        for all in allcash:
                            fclcash = all.clcash     

                        message = ftranstype+" / "+ fpaymode+" / "+fbankac+" /Rs. "+fcashrec+" / "+"Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundinoth/')
                    
                else:
                        return render(request, 'admssapp/fundinoth.html' , context)



#######################
####### FUND OUT ######
#######################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundout(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode,status="A").values('personcode','personname').distinct().order_by('personname')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                         }

                if request.method == "POST":

                        fpersoncode = request.POST.get('personcode')
                        personmaster = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)
                        allactive = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,status="A",drcr='C').order_by('id')
                        fpersoncode = personmaster.personcode
                        fpersonname = personmaster.personname
                                            
                        context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'allactive':allactive,
                            'fpersoncode':fpersoncode,
                            'fpersonname':fpersonname,
                            }

                        return render(request, 'admssapp/fundoutlist.html' , context)
                    
                else:
                        return render(request, 'admssapp/fundout.html' , context)



######################
#### FUND OUT GET ####
######################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def investorpaymentfundget(request,transid):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                clcash = allcash[0].clcash
                clbank = allbank[0].clbank


                allfund = Fundmaster.objects.get(locationcode=loginlocationcode,id=transid)

                ftransid = allfund.transid
                fpersoncode = allfund.personcode 
                fpersonname = allfund.personname 
                ftransnm =  allfund.transnm 
                ftranscd =  allfund.transcd 
                famount = allfund.amount
                fdate = allfund.date
                fmis = allfund.mis

                num_months = (loginrundate.year - fdate.year) * 12 + (loginrundate.month - fdate.month)

                fintrate = 12
                ffundtype = 'FIXED'

                if fmis == 'N':
                    fintrate = 14
                    ffundtype = 'FIXED'
                elif fmis == 'Y':
                    fintrate = 12
                    ffundtype = 'MIS'

                ftmpintrest = 0
                fintrest = 0
                counter = 0
                fpayamt = 0
                if fmis == "Y":
                    famount = allfund.misamount
                else:

                    while counter < num_months:
                        ftmpintrest = (famount + fintrest) *((fintrate/12)/100)
                        fintrest = fintrest + ftmpintrest
                        counter = counter + 1
                        
                        
                fintrest = int(fintrest)

            
                context={'loginlocationcode':loginlocationcode,
                         'loginlocationname':loginlocationname,
                         'loginrundate':loginrundate,
                         'loginstatus':loginstatus,
                         'currdate':currdate,
                         'ftransid':ftransid,
                         'ftranscd':ftranscd,
                         'ftransnm':ftransnm,
                         'famount':famount,
                         'fintrest':fintrest,
                         'fpayamt': fpayamt,
                         'fintrest':fintrest,
                         'ffundtype':ffundtype,
                         'fpersoncode':fpersoncode,
                         'fpersonname':fpersonname,
                         'allbank':allbank,
                         'clcash':clcash,
                         'clbank':clbank,
                         
                            }

                return render(request, 'admssapp/fundoutget.html' , context)            
                      


#########################
#### FUND OUT COMMIT ####
#########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def investorpaymentfundcommit(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                clcash = allcash[0].clcash


                if request.method == "POST" and request.POST.get('checkbox') is not None:

                        ffundid = request.POST.get('transid')
                        fintrest = request.POST.get('intrest')
                        fcashrec = request.POST.get('cashrec')
                        fpaymode = request.POST.get('paymode').upper()
                        fappbankac = request.POST.get('appbankac')
                        fappbankchq = request.POST.get('appbankchq')
                        fcheckbox = request.POST.get('checkbox')
                        
                        fclbank = 0
                        fbankac = "                "
                        fclcash = 0

                        allfund = Fundmaster.objects.get(locationcode=loginlocationcode,transid=ffundid)

                        fpersondesig = allfund.persondesig
                        fpersontype = allfund.persontype
                        fftransid = allfund.transid
                        fpersoncode = allfund.personcode 
                        fpersonname = allfund.personname 
                        ftransnm_m =  allfund.transnm 
                        ftranscd_m =  allfund.transcd 
                        famount = allfund.amount
                        fdate = allfund.date
                        fmis = allfund.mis
                        num_months = (loginrundate.year - fdate.year) * 12 + (loginrundate.month - fdate.month)

                        if fmis == "Y":
                            famount = allfund.misamount

                      
                        fintrest = int(fintrest)      
                        fcashrec = int(fcashrec)   
                        
                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            


                        fdrcr = "D"
                        fnarr = "FUND OUT/"+ftransnm_m.strip()+"/"+fpersonname.strip()
                        fnarr1 = "FUND OUT / "+ftransnm_m.strip()+" / "+fpersonname.strip()

                        if fpaymode=="BANK":
        
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname


                            trans = Transcd.objects.get(transcd=ftranscd_m)
                            ftrans = trans.id    
                            
                            
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id

                            if int(fcashrec + fintrest) <= fclbank:

                                if int(fcashrec) > 0:

                                    db = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,transid=ftransid,
                                        transcd=ftranscd_m,transnm=ftransnm_m,
                                        bankac=fbankac,
                                        loanid=fftransid,
                                        mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                        narration=fnarr,amount=fcashrec,drcr="D", trans_id = ftrans,
                                        clcashbank_id = opclid)
                    
                                    db.save()
                                    
                                    trans = Transcd.objects.get(transcd=fbankcode)
                                    ftrans = trans.id    

                                    db = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,transid=ftransid,
                                        transcd=fbankcode,transnm=fbankname,
                                        loanid=fftransid,
                                        bankac=fbankac,
                                        mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                        narration=fnarr,amount=fcashrec+fintrest,drcr="C", trans_id = ftrans,
                                        clcashbank_id = opclid)
                    
                                    db.save()      
                      

                            if int(fintrest) > 0:

                                ftranscd = '3346'
                                ftransnm = 'REIMBURSEMENT OF INTREST TO LENDERS'
                                                                
                                trans = Transcd.objects.get(transcd=ftranscd)
                                ftrans = trans.id    
   
                                fnarr = "FUND OUT/"+ftransnm.strip()+"/"+fpersonname.strip()
                                
                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    loanid=fftransid,
                                    bankac=fbankac,
                                    mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fintrest,drcr="D", trans_id = ftrans,
                                    clcashbank_id = opclid)
                
                                db.save()
                               
    
                                trans = Transcd.objects.get(transcd=fbankcode)
                                ftrans = trans.id    


                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=fbankcode,transnm=fbankname,
                                    loanid=fftransid,
                                    bankac=fbankac,
                                    mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec+fintrest,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
                
                                db.save()
                                

                            allbank.clbank = allbank.clbank - (int(fcashrec)+int(fintrest))
                            allbank.save()


                        if fpaymode=="CASH":

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    
                            for all in allcash:
                                fclcash = all.clcash

                            trans = Transcd.objects.get(transcd=ftranscd_m)
                            ftrans = trans.id 

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            
                            if int(fcashrec + fintrest) <= fclcash:

                                if int(fcashrec) > 0:
                                    db = Daybook(locationcode=loginlocationcode,
                                            locationname=loginlocationname,
                                            date=loginrundate,transid=ftransid,
                                            transcd=ftranscd_m,transnm=ftransnm_m,
                                            loanid=fftransid,
                                            mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                            narration=fnarr,amount=fcashrec,drcr="D", trans_id = ftrans,
                                            clcashbank_id = opclid)
                
                                    db.save()
                                
                                if int(fintrest) > 0:
                                    
                                    ftranscd = '3346'
                                    ftransnm = 'REIMBURSEMENT OF INTREST TO LENDERS'
                                    fnarr = "FUND OUT/"+ftransnm.strip()+"/"+fpersonname.strip()

                                    trans = Transcd.objects.get(transcd=ftranscd)
                                    ftrans = trans.id    
                                    
                                    db = Daybook(locationcode=loginlocationcode,
                                        locationname=loginlocationname,
                                        date=loginrundate,transid=ftransid,
                                        transcd=ftranscd,transnm=ftransnm,
                                        loanid=fftransid,
                                        mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                        narration=fnarr,amount=fintrest,drcr="D", trans_id = ftrans,
                                        clcashbank_id = opclid)
                    
                                    db.save()
            
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                            for all in allcash:
                                all.clcash = all.clcash - (int(fcashrec)+int(fintrest))
                                all.save()
                                
                        allfund.intrestamount = int(fintrest)
                        allfund.lastintpaydate = loginrundate
                        
                       
                        if famount == fcashrec: 
                            allfund.status = 'C'
                            allfund.save()
                        else:
                            allfund.status = 'A'
                            allfund.misamount = allfund.misamount - fcashrec
                            allfund.save()
                         
                            
                        fm = Fundmaster(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date = loginrundate,transid = ftransid,
                                    transcd = ftranscd_m,transnm = ftransnm_m,
                                    bankac = fbankac,
                                    mode = fpaymode,
                                    personcode = fpersoncode,
                                    personname = fpersonname,
                                    persondesig = fpersondesig,
                                    persontype = fpersontype,
                                    amount = fcashrec,
                                    drcr = fdrcr)

                        fm.save()
                        ftranstype = fnarr1
                        fcashrec = (int(fcashrec)+int(fintrest))

                        for all in allcash:
                            fclcash = all.clcash     

                        message = ftranstype+" / "+ fpaymode+" / "+fbankac+" /Rs. "+str(fcashrec)+" / "+"Processed Succesfully"

                        if int(fcashrec)==0 and int(fintrest)==0:
                            message = ''


                        messages.success(request, message)
                        return HttpResponseRedirect('/fundout/')
                    
                else:
                        return render(request, 'admssapp/fundout.html' , context)


########################
####### FUND LOAN ######
########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundloan(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
 

                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank="Y")
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allperson = Personmaster.objects.filter(locationcode=loginlocationcode,persontype__in=['DIR','ACH','INV']).distinct('personname').order_by('personname')


                clcash = allcash[0].clcash
                clbank = allbank[0].clbank

                    
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                        'allbank':allbank,
                        'clcash':clcash,
                        'clbank':clbank,
                         }

                if request.method == "POST":

                        fpersoncode = request.POST.get('personcode')
                        fcashrec = request.POST.get('cashrec')
                        fpaymode = request.POST.get('paymode')
                        fbankac = request.POST.get('appbankac')
                        fbankchq = request.POST.get('appbankchq')
                        fcheckbox = request.POST.get('checkbox')
                        fremark = request.POST.get('remark')
                        
                        ffundcode = '3374'
                        
                     
                        
                        personmaster = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)
                        fpersoncode = personmaster.personcode
                        fpersonname = personmaster.personname
                        
                    
                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        trans = Transcd.objects.get(transcd=ffundcode)
                        ftranscd = trans.transcd
                        ftransnm = trans.transnm

                        person = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fpersoncode)
                        fpersoncode=person.personcode
                        fpersonname=person.personname
                        fpersondesig = person.persondesig
                        fpersontype = person.persontype
                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            

                        fdrcr = "C"
                        fnarr = "General Loan/"+ftransnm.strip()+"/"+fpersonname.strip()
                        fnarr1 = "General Loan/ "+ftransnm.strip()+" / "+fpersonname.strip()
        

                        if fpaymode=="BANK":
                            

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            clbank = allbank.clbank

                            
                            if clbank < int(fcashrec):
                                message = "Not Sufficient Bank Balance for Payment of "+ftransnm.strip() + " Rs. "+str(fcashrec).strip()+" Bank is Rs. "+str(clbank).strip()
                                messages.success(request, message)
                                return HttpResponseRedirect('/fundloan/')
                            
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname


                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                chequeno=fbankchq,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="D", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id    

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=fbankcode,transnm=fbankname,
                                bankac=fbankac,
                                chequeno=fbankchq,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()

                            allbank.clbank = allbank.clbank - int(fcashrec)
                            allbank.save()



                        if fpaymode=="CASH":
                            
                            fclbank = 0
                            fbankac = "                "
                            fclcash = 0

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)[0]
                            clcash = allcash.clcash
                    
                                
                            if clcash < int(fcashrec):
                                message="Not Sufficient Cash Balance for Payment of "+ftransnm.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()
                                messages.success(request, message)
                                return HttpResponseRedirect('/fundloan/')
                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id    

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id

                            db = Daybook(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                date=loginrundate,transid=ftransid,
                                transcd=ftranscd,transnm=ftransnm,
                                bankac=fbankac,
                                mode=fpaymode,personcode=fpersoncode,personname=fpersonname,
                                narration=fnarr,amount=fcashrec,drcr="C", trans_id = ftrans,
                                clcashbank_id = opclid)
            
                            db.save()
            
                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - int(fcashrec)
                                all.save()
                                            


                        gen = Generalloanmaster(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,
                                         transid=ftransid,
                                         transcd=ftranscd,
                                         transnm=ftransnm,
                                         bankac=fbankac,
                                         chequeno=fbankchq,
                                         mode=fpaymode,
                                         personcode=fpersoncode,
                                         personname=fpersonname,
                                         remark=fremark,
                                         dramount=fcashrec,
                                         balamount=fcashrec,
                                         status="A")
                        gen.save()



                        message = "General Loan / "+fpersonname+" / "+ fpaymode+" / "+fbankac+" /Rs. "+fcashrec+" / "+"Processed Succesfully through "+fpaymode

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundloan/')
                    
                else:
                        return render(request, 'admssapp/fundloan.html' , context)


############################
#### FUND LOAN RECOVERY ####
############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundloanrecovery(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                allloan = Generalloanmaster.objects.filter(locationcode=loginlocationcode,status='A')
                alltotal = Generalloanmaster.objects.filter(locationcode=loginlocationcode).values('locationcode','locationname').aggregate(totalac=Coalesce(Count('transid'),0),drtotal=Coalesce(Sum('dramount'), 0),crtotal=Coalesce(Sum('cramount'),0))

     
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allloan':allloan,
                        'alltotal':alltotal
                           }

                return render(request, 'admssapp/fundloancredit.html' , context)




#################################
#### FUND LOAN RECOVERY LIST ####
#################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundloanrecoverylist(request,loanid):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                clcash = allcash[0].clcash

                allloan = Generalloanmaster.objects.get(locationcode=loginlocationcode,id=loanid)
                
                fpersoncode = allloan.personcode 
                fpersonname = allloan.personname 
                ftransnm =  allloan.transnm 
                fdramount = allloan.dramount
                fcramount = allloan.cramount
                fbalamount = allloan.balamount
                fadvdate =  allloan.date
                ftransid = allloan.transid
  
 
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'fpersoncode':fpersoncode,
                        'fpersonname':fpersonname,
                        'ftransnm': ftransnm,
                        'fdramount': fdramount,
                        'fcramount' : fcramount,
                        'fbalamount': fbalamount,
                        'fadvdate': fadvdate,
                        'ftransid':ftransid,
                        'allbank':allbank,
                        
                         }
            
                return render(request, 'admssapp/fundloancreditcommit.html' , context)



###################################
#### FUND LOAN RECOVERY COMMIT ####
###################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundloanrecoverycommit(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:



                if request.method == "POST":

                    floanid = request.POST.get('transid')

                    fcashrec = int(request.POST.get('cashrec'))
                    fmode = request.POST.get('emimode').upper()
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                    fbankac = ''


                    allloan = Generalloanmaster.objects.get(locationcode=loginlocationcode,transid=floanid)
                
                    ftransnm = allloan.transnm
                    
                    ftranscd = allloan.transcd
                    
                    fpersoncode = allloan.personcode
                    
                    fpersonname = allloan.personname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    fcashrec = int(fcashrec)

                    allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    clcash = allcash[0].clcash
    

                    alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                    mtransidnum = alllocmast.transidnum + 1
                    alllocmast.transidnum = alllocmast.transidnum + 1
                    alllocmast.save()

                    yy = loginrundate.strftime("%Y")
                    yy = yy[0:2]
                    mm = loginrundate.strftime("%m")
                    dd = loginrundate.strftime("%d")
                    

                    ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
           
                
                    fnarr = "Fund Loan Recovery/"+ftransnm.strip()+"/"+fpersonname.strip()
                    if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="C",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash + int(fcashrec)
                                all.save()
                            message="Fund Loan Recovery of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                    if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id


                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="C",trans_id = ftrans,  clcashbank_id = opclid
                                    )
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="D",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank=allbank.clbank + int(fcashrec)
                            allbank.save()

                            message="Advance Payment Recovery of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                    adv = Generalloantrans(locationcode=loginlocationcode,
                                         locationname=loginlocationname,
                                         date=loginrundate,
                                         loanid = allloan.transid,
                                         transid=ftransid,
                                         transcd=ftranscd,
                                         transnm=ftransnm,
                                         bankac=fbankac,
                                         chequeno=fappbankchq,
                                         mode=fmode,
                                         personcode=fpersoncode,
                                         personname=fpersonname,
                                         amount=fcashrec,
                                         drcr="C",
                                         master_id = allloan.id)
                    adv.save()
                    
                    allloan.cramount = allloan.cramount + fcashrec
                    allloan.balamount = allloan.balamount - fcashrec
                    
                    if allloan.dramount == allloan.cramount:
                       allloan.status = 'C'
                    
                    allloan.save()
                    
                    success = True
            
                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
                
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    locationstatus=ll.status

                    messages.success(request, message)
                    return HttpResponseRedirect('/fundloanrecovery/')




##############################
#### MIS PAYMENT INVESTOR ####
##############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundpayment(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


 
                allinvestor = Fundmaster.objects.filter(locationcode=loginlocationcode).distinct('personname').order_by('personname')
                allinvestor = Fundmaster.objects.filter(locationcode=loginlocationcode, mis='Y',intduedate__lte=loginrundate, drcr='C', status='A').distinct('personname').order_by('personname')
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allinvestor': allinvestor,
                        }

                
            
                if request.method == "POST":
            
                    fpersoncode = request.POST.get('personname')
                    fpaymenttype = request.POST.get('paymenttype')

                    if fpaymenttype == "MIS":
                        fundmast = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,mis='Y',intduedate__lte=loginrundate,drcr='C',status='A')

                    person = Fundmaster.objects.filter(personcode=fpersoncode).distinct('personcode')
                    fpersonname=person[0].personname

                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
         

                    context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'loginstatus':loginstatus,
                             'currdate':currdate,
                             'allbank':allbank,
                             'fundmast':fundmast,
                             'fpaymenttype': fpaymenttype,
                             'fpersoncode':fpersoncode,
                             'fpersonname':fpersonname,
                               }                       

                    return render(request, 'admssapp/fundpaymentget.html' , context)
            
                else:
                    return render(request, 'admssapp/fundpayment.html' , context)



############################
##### MIS PAYMENT GET ######
############################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundpaymentget(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                if request.method == "POST":

                    fpersoncode = request.POST.get('personname')
                    fpaymenttype = request.POST.get('paymenttype')
                    ffundtransid = request.POST.get('fundtransid')

                    fundmast = Fundmaster.objects.get(locationcode=loginlocationcode, personcode=fpersoncode, transid=ffundtransid, drcr='C', status='A')

                    famount = fundmast.amount
                    fmisamount = fundmast.misamount
                    ffundid = fundmast.transid


                    person = Fundmaster.objects.filter(personcode=fpersoncode).distinct('personcode')
                    fpersonname=person[0].personname
                    #allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                    #clcash = allbank[0].clcash
                    #clbank = allbank[0].clbank  

                    allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                    clcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)[0].clcash
                    clbank = allbank[0].clbank


                    if fpaymenttype == 'MIS':
                        fint = fundmast.intrate
                        fpayamount = fmisamount*fint/100
                        flastpaydate = fundmast.lastintpaydate
                        fintduedate = fundmast.intduedate


                        context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'loginstatus':loginstatus,
                             'currdate':currdate,
                             'allbank':allbank,
                             'famount':famount,
                             'fpayamount':fpayamount,
                             'fpaymenttype': fpaymenttype,
                             'fpersoncode':fpersoncode,
                             'fpersonname':fpersonname,
                             'ffundtransid':ffundtransid,
                             'flastpaydate':flastpaydate,
                             'ffundid':ffundid,
                             'fintduedate':fintduedate,
                             'loginrundate':loginrundate,
                             'clcash':clcash,
                             'clbank':clbank,
                                 }          
    
                        return render(request, 'admssapp/fundpaymentcommitMIS.html' , context)

                    elif fpaymenttype == 'REPAYMENT':
                        fpayamount = fmisamount
                        ffunddate = fundmast.date

                        context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'loginstatus':loginstatus,
                             'currdate':currdate,
                             'allbank':allbank,
                             'famount':famount,
                             'fpayamount':fpayamount,
                             'fpaymenttype': fpaymenttype,
                             'fpersoncode':fpersoncode,
                             'fpersonname':fpersonname,
                             'ffundtransid':ffundtransid,
                             'ffundid':ffundid,
                             'loginrundate':loginrundate,
                             'clcash':clcash,
                             'clbank':clbank,
                                 }          
                        return render(request, 'admssapp/fundpaymentcommitREPAYMENT.html' , context)



##############################
##### MIS PAYMENT COMMIT #####
##############################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundpaymentcommit(request):
    

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         locationstatus=ll.status
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:


                    fpersoncode = request.POST.get('personname')
                    fpaymenttype = request.POST.get('paymenttype')
                    fpayamount = request.POST.get('payamount')
                    ffundtransid = request.POST.get('fundtransid')

                    fmode = request.POST.get('emimode')
                    fappbankac = request.POST.get('appbankac')
                    fappbankchq = request.POST.get('appbankchq')
                   
 
                    if fpaymenttype == 'MIS':
                        fundmast = Fundmaster.objects.get(locationcode=loginlocationcode, personcode=fpersoncode, transid=ffundtransid, drcr='C', status='A')

                        famount = fundmast.amount
                        fint = fundmast.intrate
                        fmisamount = fundmast.misamount
                        fcashrec = fmisamount*fint/100
                        ffundid = fundmast.transid
                        fpersoncode=fundmast.personcode
                        fpersonname=fundmast.personname
                        ffundmast = fundmast.id
                        fduedate = fundmast.intduedate




                        ftranscd = '3346'
                        ftransnm = 'REIMBURSEMENT OF INTREST TO LENDERS'


                        if fduedate > loginrundate:

                           message="MIS Not Due ..."
                           messages.success(request, message)
                           return HttpResponseRedirect('/fundpayment/')


                    
         
                        cashbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        clcash = cashbank[0].clcash



                        if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            clbank = allbank.clbank

            
                        if fmode == "CASH" and fcashrec > clcash:

                            success = True

                            message="Not Sufficient Cash to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/fundpayment/')

                        if fmode == "BANK" and fcashrec > clbank:

                            success = True

                            message="Not Sufficient Fund in Bank to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Bank Balance is Rs. "+str(clbank).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/fundpayment/')


                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()



                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    

                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
                
                        fnarr = "MIS Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                        if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id
                            fbankac = ''

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    loanid = ffundid,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
                        
                            db.save()

            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - fcashrec
                                all.save()
                            message="Payment of MIS "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                        if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id

                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    loanid = ffundid,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                loanid = ffundid,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank = allbank.clbank - fcashrec
                            allbank.save()

                            message="Payment of MIS "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                        db = Fundtrans(locationcode=loginlocationcode,
                                 locationname=loginlocationname,
                                 date=loginrundate,transid=ftransid,
                                 transcd=ftranscd,transnm=ftransnm,
                                 bankac=fbankac,
                                 fundid = ffundid,
                                 mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                 amount=fcashrec,drcr="D",fundmast_id = ffundmast)
            
                        db.save()

               
                        days_in_month = calendar.monthrange(fduedate.year, fduedate.month)[1]
                        fintduedate = fduedate + timedelta(days=days_in_month)
 
   
                        fundmast = Fundmaster.objects.get(locationcode=loginlocationcode, personcode=fpersoncode, transid=ffundtransid, drcr='C', status='A')
                        fundmast.lastintpaydate = loginrundate
                        fundmast.intduedate = fintduedate
                        fundmast.mispaid = fundmast.mispaid + fcashrec

                        fundmast.save()

                        success = True
            
                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

 
                        messages.success(request, message)
                        return HttpResponseRedirect('/fundpayment/')


                    if fpaymenttype == 'REPAYMENT':
                        fundmast = Fundmaster.objects.get(locationcode=loginlocationcode, personcode=fpersoncode, transid=ffundtransid, drcr='C', status='A')

                        famount = fundmast.amount
                        fmisamount = fundmast.misamount
                        fcashrec = int(fpayamount)
                        ffundid = fundmast.transid
                        fpersoncode=fundmast.personcode
                        fpersonname=fundmast.personname
                        fpersondesig = fundmast.persondesig
                        fpersontype = fundmast.persontype

                        ffundmast = fundmast.id

                        ftranscd = fundmast.transcd
                        ftransnm = fundmast.transnm


                        if fcashrec > fmisamount:

                            message="Amount is not correct"
                            messages.success(request, message)
                            return HttpResponseRedirect('/fundpayment/')

         
                        cashbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                        clcash = cashbank[0].clcash



                        if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            clbank = allbank.clbank

            
                        if fmode == "CASH" and fcashrec > clcash:

                            success = True

                            message="Not Sufficient Cash to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Cash is Rs. "+str(clcash).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/fundpayment/')

                        if fmode == "BANK" and fcashrec > clbank:

                            success = True

                            message="Not Sufficient Fund in Bank to make Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" Bank Balance is Rs. "+str(clbank).strip()

                            messages.success(request, message)
                            return HttpResponseRedirect('/fundpayment/')


                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()



                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    

                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
                
                        fnarr = "Payment/"+ftransnm.strip()+"/"+fpersonname.strip()
                        if fmode == "CASH":

                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id
                            fbankac = ''

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                            opclid = allcash.id
                                
                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fappbankac,
                                    loanid = ffundid,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()
            

                            allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                            for all in allcash:
                                all.clcash = all.clcash - fcashrec
                                all.save()
                            message="Payment of "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Cash..."


                    
                        if fmode == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fbankac = allbank.bankac
                            fbankacname=allbank.bankacname
                            fbankcode=allbank.bankcode
                            fbankname=allbank.bankname

                            
                            trans = Transcd.objects.get(transcd=ftranscd)
                            ftrans = trans.id

                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                            opclid = allbank.id

                            db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    loanid = ffundid,
                                    chequeno=fappbankchq,
                                    mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                    narration=fnarr,amount=fcashrec,drcr="D",trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                            db.save()


                            trans = Transcd.objects.get(transcd=fbankcode)
                            ftrans = trans.id
                    
                            db1 = Daybook(locationcode=loginlocationcode,
                                date=loginrundate,
                                locationname=loginlocationname,
                                transid=ftransid,transcd=fbankcode,transnm=fbankname,
                                mode=fmode,personcode=fpersoncode,personname=fpersonname,
                                bankac=fbankac,
                                loanid = ffundid,
                                chequeno=fappbankchq,
                                narration=fnarr,amount=int(fcashrec),drcr="C",trans_id = ftrans,
                                clcashbank_id = opclid)

                            db1.save()


                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            allbank.clbank = allbank.clbank - fcashrec
                            allbank.save()

                            message="Payment of MIS "+fpersonname.strip()+" Rs. "+str(fcashrec).strip()+" for "+ftransnm.strip()+" Processed successfully by Bank..."

                        db = Fundmaster(locationcode=loginlocationcode,
                                 locationname=loginlocationname,
                                 date=loginrundate,transid=ftransid,
                                 transcd=ftranscd,transnm=ftransnm,
                                 bankac=fbankac,
                                 mode=fmode,
                                 personcode=fpersoncode,
                                 personname=fpersonname,
                                 persondesig = fpersondesig,
                                 persontype = fpersontype,
                                 amount=fcashrec,
                                 drcr="D")
            
                        db.save()

 
   
                        fundmast = Fundmaster.objects.get(locationcode=loginlocationcode, personcode=fpersoncode, transid=ffundtransid, drcr='C', status='A')
                        fundmast.misamount = fundmast.misamount - fcashrec
                        if fundmast.misamount == 0:
                            fundmast.status = 'C'
                              
   
                        fundmast.save()

                        success = True
            
                        loguserid = request.session['loguserid']
                        ll=Locationlogin.objects.get(user=loguserid)
                
                        loginlocationcode=ll.locationcode
                        loginlocationname=ll.locationname
                        loginrundate=ll.rundate
                        locationstatus=ll.status

 
                        messages.success(request, message)
                        return HttpResponseRedirect('/fundpayment/')



############################
#### ACTIVE FUND REPORT ####
############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundactivereport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode).distinct('personname')
            
                #ffromdate = datetime.strptime('2019-10-05', '%Y-%m-%d').date()
                #ffromdate = datetime.strptime('20191003','%Y%m%d')
                #ftodate = ll.rundate
                
                #activefund = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A', drcr='C').order_by('personname','date')
                #summactivefund = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A', drcr='C').values('locationcode').annotate(totamt=Coalesce(Sum('amount'),0))           
                #activefund = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',drcr='C').order_by('misamount', 'personname', 'date')
                #subtotal = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A', drcr='C').values('misamount').annotate(totamt=Coalesce(Sum('amount'), 0)).order_by('misamount')
                #grandtotal = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',drcr='C').aggregate(totamt=Coalesce(Sum('amount'), 0))

                
                 
                #context={'loginlocationcode':loginlocationcode,
                #        'loginlocationname':loginlocationname,
                #        'loginrundate':loginrundate,
                #        'loginstatus':loginstatus,
                #        'currdate':currdate,
                #        'activefund':activefund,
                #        'subtotal':subtotal,
                #        'grandtotal':grandtotal,
                #        }
                #return render(request, 'admssapp/fundactivereport.html', context)


                activefund_qs = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',drcr='C').order_by('personname', 'date')

                activefund = []
                prev_person = None
                subtotal_amt = 0
                subtotal_misamt = 0
                sn = 1

                for row in activefund_qs:

                    if prev_person is not None and prev_person != row.personname:
                        activefund.append({
                            'is_subtotal': True,
                            'personname': prev_person,
                            'subtotal': subtotal_amt,
                            'subtotal_misamt': subtotal_misamt,
                        })
                        subtotal_amt = 0
                        subtotal_misamt = 0

                    activefund.append({
                        'is_subtotal': False,
                        'sn': sn,
                        'personname': row.personname,
                        'date': row.date,
                        'transid': row.transid,
                        'transnm': row.transnm,
                        'relatedpersonname': row.relatedpersonname,
                        'amount': row.amount,
                        'misamount':row.misamount,
                        'mis': row.mis,
                        'drcr': row.drcr,
                    })

                    subtotal_amt += row.amount or 0
                    subtotal_misamt += row.misamount or 0

                    prev_person = row.personname
                    sn += 1

                # this must be outside for loop
                if prev_person is not None:
                    activefund.append({
                        'is_subtotal': True,
                        'personname': prev_person,
                        'subtotal': subtotal_amt,
                        'subtotal_misamt': subtotal_misamt,
                    })

                grandtotal = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',drcr='C').aggregate(totamt=Coalesce(Sum('amount'), 0),totmisamt=Coalesce(Sum('misamount'), 0))
                context = {
                    'loginlocationcode': loginlocationcode,
                    'loginlocationname': loginlocationname,
                    'loginrundate': loginrundate,
                    'loginstatus': loginstatus,
                    'currdate': currdate,
                    'activefund': activefund,
                    'grandtotal_amt': grandtotal['totamt'],
                    'grandtotal_misamt': grandtotal['totmisamt'],
                }

                return render(request, 'admssapp/fundactivereport.html', context)

###########################
#### MIS ACTIVE REPORT ####
###########################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundmisactivereport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode).distinct('personname')
            
                #ffromdate = datetime.strptime('2019-10-05', '%Y-%m-%d').date()
                #ffromdate = datetime.strptime('20191003','%Y%m%d')
                #ftodate = ll.rundate
                
                activefund = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',mis='Y').order_by('intduedate','personname','date')
                summactivefund = Fundmaster.objects.filter(locationcode=loginlocationcode,status='A',mis='Y').values('locationcode').annotate(totamt=Coalesce(Sum('amount'),0)).annotate(mistotamt=Coalesce(Sum('misamount'),0))                
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'activefund':activefund,
                        'summactivefund':summactivefund,
                            }
                return render(request, 'admssapp/fundmisactivereport.html', context)


#################################
#### FUND TRANSACTION REPORT ####
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransactionreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode).distinct('personname')
            
                #ffromdate = datetime.strptime('2019-10-05', '%Y-%m-%d').date()
                ffromdate = datetime.strptime('20191003','%Y%m%d')
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    fpersoncode = request.POST.get('personcode')
                    ffromdate = request.POST.get('fromdate')
                    ftodate=request.POST.get('todate')          

                    name_code = Fundmaster.objects.filter(personcode = fpersoncode)[0]
                    fpersonname = name_code.personname
                    allfund = Fundmaster.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fpersoncode).order_by('date','id')

                    allfundin = Fundmaster.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fpersoncode,drcr='C').values('personcode','personname','drcr').annotate(totac=Count('personcode'),totamt=Coalesce(Sum('amount'),0))
                    allfundout = Fundmaster.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, personcode=fpersoncode, drcr='D').values(
                        'personcode', 'personname', 'drcr').annotate(totac=Count('personcode'), totamt=Coalesce(Sum('amount'), 0))
            
                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'allfund':allfund,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'fpersoncode':fpersoncode,
                                    'fpersonname':fpersonname,
                                    'allfundin':allfundin,
                                    'allfundout':allfundout,
                        
                                        }
                
                    return render(request, 'admssapp/fundtransactionreportshow.html', context)
                else:
                    return render(request, 'admssapp/fundtransactionreport.html', context)




#####################################
#### EMI FUND TRANSACTION REPORT ####
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emifundtransactionreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode,mis='Y').distinct('personname')
            
                #ffromdate = datetime.strptime('2019-10-05', '%Y-%m-%d').date()
                ffromdate = datetime.strptime('20191003','%Y%m%d')
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    fpersoncode = request.POST.get('personcode')

                    name_code = Fundmaster.objects.filter(personcode = fpersoncode)[0]

                    fpersonname = name_code.personname

                    allfund = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,mis='Y').order_by('date','id')
                    fundsumm = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,mis='Y').aggregate(totalac=Coalesce(Count('personcode'),0),totalamt=Coalesce(Sum('amount'),0),totalmis=Coalesce(Sum('misamount'),0))

                    totalamt = fundsumm.get('totalamt')
                    totalmis = fundsumm.get('totalmis')

                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'allfund':allfund,
                                    'fpersoncode':fpersoncode,
                                    'fpersonname':fpersonname,
                                    'totalamt':totalamt,
                                    'totalmis':totalmis,
                                        }
                
                    return render(request, 'admssapp/fundemitransactionreportshow.html', context)
                else:
                    return render(request, 'admssapp/fundemitransactionreport.html', context)


#####################################
#### EMI FUND TRANSACTION REPORT ####
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emifundtransactionreport(request):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         
                allperson = Fundmaster.objects.filter(locationcode=loginlocationcode,mis='Y').distinct('personname')
            
                #ffromdate = datetime.strptime('2019-10-05', '%Y-%m-%d').date()
                ffromdate = datetime.strptime('20191003','%Y%m%d')
                ftodate = ll.rundate
            
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'allperson':allperson,
                        'ffromdate':ffromdate,
                        'ftodate':ftodate,
                            }
        
            
                if request.method == "POST":
                    fpersoncode = request.POST.get('personcode')

                    name_code = Fundmaster.objects.filter(personcode = fpersoncode)[0]

                    fpersonname = name_code.personname

                    allfund = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,mis='Y').order_by('date','id')
                    fundsumm = Fundmaster.objects.filter(locationcode=loginlocationcode,personcode=fpersoncode,mis='Y').aggregate(totalac=Coalesce(Count('personcode'),0),totalamt=Coalesce(Sum('amount'),0),totalmis=Coalesce(Sum('misamount'),0))

                    totalamt = fundsumm.get('totalamt')
                    totalmis = fundsumm.get('totalmis')

                    context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'loginstatus':loginstatus,
                                    'currdate':currdate,
                                    'allfund':allfund,
                                    'fpersoncode':fpersoncode,
                                    'fpersonname':fpersonname,
                                    'totalamt':totalamt,
                                    'totalmis':totalmis,
                                        }
                
                    return render(request, 'admssapp/fundemitransactionreportshow.html', context)
                else:
                    return render(request, 'admssapp/fundemitransactionreport.html', context)



#####################################
#### EMI FUND TRANSACTION LEDGER ####
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def emifundtransactionledger(request,fundid):
     

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
         

                funddata=Fundmaster.objects.get(id=fundid)
                
                ffundid = funddata.transid
                fname = funddata.personname
                fcode = funddata.personcode
                fdate = funddata.date
                famount = funddata.amount
                fmisamount = funddata.misamount
                fintduedate = funddata.intduedate
                flastemipaydate = funddata.lastintpaydate

                fundtrans = Fundtrans.objects.filter(fundid=ffundid).order_by('date')

                fundsumm = Fundtrans.objects.filter(fundid=ffundid).aggregate(totalac=Coalesce(Count('transid'),0),totalamt=Coalesce(Sum('amount'),0))
                totalamt = fundsumm.get('totalamt')


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate':currdate,
                        'ffundid':ffundid,
                        'fname':fname,
                        'fcode':fcode,
                        'fdate':fdate,
                        'famount':famount,
                        'fmisamount':fmisamount,
                        'fintduedate':fintduedate,
                        'flastemipaydate':flastemipaydate,
                        'fundtrans':fundtrans,
                        'totalamt':totalamt,
                          }
 
                return render(request, 'admssapp/fundemitransactionledger.html', context)




##############################################
######## COLL EMI  AMOUNT MODIFICATIONS ######
##############################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemidepositupdate(request,emicolldata_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:

            collcorrdata=Emicolldata.objects.get(id=emicolldata_id)
            floanid=collcorrdata.loanid
            fappname=collcorrdata.master.appname
            femiduedate=collcorrdata.master.appemiduedate
            flastemidepdate=collcorrdata.master.applastemidepdate
            fdelaydays=collcorrdata.delaydays
            fdate=collcorrdata.date
            famount=collcorrdata.amount
            flatefee=collcorrdata.latefee
            fdelayamount = collcorrdata.delayamount
            femiamount=collcorrdata.master.apploanemi


        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'floanid':floanid,
                    'fappname':fappname,
                    'femiduedate':femiduedate,
                    'flastemidepdate':flastemidepdate,
                    'fdelaydays':fdelaydays,
                    'famount':famount,
                    'fdate':fdate,
                    'flatefee':flatefee,
                    'femiamount':femiamount,
                    'fdelayamount':fdelayamount,
                    'emicolldata_id':emicolldata_id,
                        }


            if collcorrdata==None:
                pass
            else:
                return render(request,"admssapp/collemiupdate.html", context)




###########################################
####### GENERATED FUND TRANSFER SEND ######
###########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransfersend(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                for all in allcash:
                    fclcash = all.clcash
                
                ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0)
                ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('hqamount'), 0))
                famount = ispaidsumm.get("amt")

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'allbank':allbank,
                        'fclcash':fclcash,
                        'ispaid':ispaid,
                        'ispaidsumm':ispaidsumm,
                        'famount':famount,

                          }

                if request.method == "POST":


                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0)
                        ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('hqamount'), 0))

                        famount = ispaidsumm.get("amt")

                        transferto = Locationlogin.objects.values('locationcode','locationname').filter(~Q(locationcode=loginlocationcode)).distinct().order_by('locationname') 


                        context={'loginlocationcode':loginlocationcode,
                                 'loginlocationname':loginlocationname,
                                 'loginrundate':loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate':currdate,
                                 'allbank':allbank,
                                 'fclcash':fclcash,
                                 'ispaid':ispaid,
                                 'ispaidsumm':ispaidsumm,
                                 'famount':famount,
                                 'transferto':transferto,

                                   }


                        return render(request, 'admssapp/fundtransfersendcommit.html' , context)                    

                else:
                        return render(request, 'admssapp/fundtransfersend.html' , context)




##################################################
####### GENERATED FUND TRANSFER SEND COMMIT ######
##################################################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransfersendcommit(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
 

                if request.method == "POST" and request.POST.get('checkbox') is not None:



                        famount = request.POST.get('amount')
                        ftransferto = request.POST.get('transferto')
                        fpaymode = request.POST.get('paymode')
                        fappbankac = request.POST.get('appbankac')
                        fcheckbox = request.POST.get('checkbox')
                        ffundtype = 'HQFEES'

                        ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0).order_by("-fromdate")
                        ffromdate = ispaid[0].fromdate
                        ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0).order_by("-todate")
                        ftodate = ispaid[0].todate

                        ispaid = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0)
                        ispaidsumm = Authcenterexpance.objects.filter(locationcode=loginlocationcode,hqpaid='N',hqamount__gt=0).aggregate(ac=Coalesce(Count('locationcode'), 0), amt=Coalesce(Sum('hqamount'), 0))
                        famount = str(ispaidsumm.get("amt"))




                        #ffromdate = datetime.strptime(ffromdate, '%Y-%m-%d')
                        #ftodate = datetime.strptime(ftodate, '%Y-%m-%d')

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname


                        trans = Transcd.objects.get(transcd=ftransferto)
                        ftrans = trans.id    
                        ftranstocd = trans.transcd
                        ftranstonm = trans.transnm          


                        if fpaymode=="BANK": 
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname

                            if fclbank < int(famount):
                                 message = "Not sufficient Fund in Bank to SEND " + ftransnm + " / Rs. " +famount 

                                 messages.success(request, message)
                                 return HttpResponseRedirect('/fundtransfersend/')

                        if fpaymode=="CASH":
                             allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                             fclcash = allcash[0].clcash

                             if fclcash < int(famount):
                                 message = "Not sufficient Fund in Cash to SEND " + ftransnm + " / Rs. " +famount 

                                 messages.success(request, message)
                                 return HttpResponseRedirect('/fundtransfersend/')

                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()


                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
   
                        if fpaymode == "BANK" and fclbank > int(famount):
                            
                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                                fclbank = allbank.clbank
                                fbankac = allbank.bankac
                                fbankcode = allbank.bankcode
                                fbankname = allbank.bankname
                     
                                fnarr = "FUND SEND/HQFEES/Rs."+famount+" Through"+fpaymode

                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                                opclid = allbank.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranstocd,transnm=ftranstonm,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    narration=fnarr, amount=famount, drcr="D", trans_id=ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                trans = Transcd.objects.get(transcd=fbankcode)
                                ftrans = trans.id    

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=fbankcode,transnm=fbankname,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
                                db.save()

                                allbank.clbank = allbank.clbank - netamt
                                allbank.save()



                        if fpaymode=="CASH" and  fclcash > int(famount):
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                                fclcash = allcash[0].clcash
                    
                                fnarr = "FUND SEND/HQFEES/Rs."+famount+" Through "+fpaymode         

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranstocd,transnm=ftranstonm,
                                    mode=fpaymode,
                                    narration=fnarr, amount=famount, drcr="D", trans_id=ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()
            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                                for all in allcash:
                                    all.clcash = all.clcash - int(famount)
                                    all.save()

                        ftranscd = '3379'
                        trans = Transcd.objects.get(transcd=ftranscd)
                        ftrans = trans.id   
                        ftransnm = trans.transnm

                        trans = Fundsendreceive(locationcode=loginlocationcode,
                               locationname=loginlocationname,
                               date=loginrundate,transid=ftransid,
                               fromdate=ffromdate,todate=ftodate,
                               translocationcode=ftranstocd, translocationname=ftranstonm,
                               mode=fpaymode,
                               transcd=ftranscd,
                               transnm=ftransnm,
                               fundtype=ffundtype,amount=famount,drcr="D",
                               status = 'A')
            
                        trans.save()

                        for x in ispaid:
                            x.hqpaid = 'Y'
                            x.hqtransid = ftransid
                            x.hqdate = loginrundate
                            x.save()


                        message = "FUND SEND to " + ftranstonm + " / Rs. " + str(famount) + " / " + "Through " + fpaymode + " Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundtransfersend/')
                    
                else:
                        return render(request, 'admssapp/fundtransfersend.html' , context)


####################################
####### FUND TRANSFER RECEIVE ######
####################################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransferreceive(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 

                fndrec = Fundsendreceive.objects.filter(translocationcode=loginlocationcode,status='A',transcd__in=['3014','3012','3379'])
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode, date=loginrundate)

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'fndrec':fndrec,
                          }

                if request.method == "POST":

                        ffundrec = request.POST.get('transferreceive')

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        fndrec = Fundsendreceive.objects.get(transid=ffundrec, status='A')

                        ffundtype = fndrec.fundtype
                        flocationname = fndrec.locationname
                        famount = fndrec.amount
                        fmode = fndrec.mode
                        fdate = fndrec.date
                        ftransid = fndrec.transid
  
                        context={'loginlocationcode': loginlocationcode,
                                 'loginlocationname': loginlocationname,
                                 'loginrundate': loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate': currdate,
                                 'ffundtype': ffundtype,
                                 'flocationname': flocationname,
                                 'famount': famount,
                                 'fmode': fmode,
                                 'fdate': fdate,
                                 'ftransid': ftransid,
                                 'allbank': allbank,
                                   }

                        return render(request, 'admssapp/fundtransferreceiveget.html', context)

                else:
                        return render(request, 'admssapp/fundtransferreceive.html' , context)



###########################################
####### FUND TRANSFER RECEIVE COMMIT ######
###########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransferreceivecommit(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
 
                if request.method == "POST":

                        ffundrec = request.POST.get('transferreceive')
                        fpaymode = request.POST.get('mode')
                        fbankac = request.POST.get('bankac')
                        fbankchq = request.POST.get('bankchq')

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        fndrec = Fundsendreceive.objects.get(transid=ffundrec, status='A')

                        ffundtype = fndrec.fundtype
                        flocationname = fndrec.locationname
                        flocationcode = fndrec.locationcode

                        famount = fndrec.amount
                        fpaymode = fndrec.mode
                        fdate = fndrec.date
                        ftransid = fndrec.transid
                        ftranscd = fndrec.locationcode
                        ftransnm = fndrec.locationname

                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)    

                        transcd = Transcd.objects.get(transcd=flocationcode)
                        ftrans = transcd.id   



                        if fpaymode == "BANK":
                            
                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                                fclbank = allbank.clbank
                                fbankac = allbank.bankac
                                fbankcode = allbank.bankcode
                                fbankname = allbank.bankname
                     
                                fnarr = "FUND RECEIVED/"+ffundtype.strip()+"/Rs."+str(famount).strip()+" Through"+fpaymode

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    chequeno=fbankchq,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                trans = Transcd.objects.get(transcd=fbankcode)
                                ftrans = trans.id    


                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=fbankcode,transnm=fbankname,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    chequeno=fbankchq,                                    
                                    narration=fnarr,amount=famount,drcr="D", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                allbank.clbank = allbank.clbank + int(famount)
                                allbank.save()

                        if fpaymode=="CASH" :
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                                fclcash = allcash[0].clcash
                    
                                fnarr = "FUND SEND/"+ffundtype.strip()+"/Rs."+str(famount).strip()+" Through "+fpaymode         

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()
            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                                for all in allcash:
                                    all.clcash = all.clcash + int(famount)
                                    all.save()

                        
                        fndrec.transtransid = ftransid
                        fndrec.transdate = loginrundate
                        fndrec.status = 'C'

                        fndrec.save()

                        message = "FUND RECEIVED From " + flocationname + " / Rs. " + str(famount) + " / " +  "Through " + fpaymode + " Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundtransferreceive/')

                        return render(request, 'admssapp/fundtransferreceiveget.html', context)
                else:
                        return render(request, 'admssapp/fundtransferreceive.html' , context)




########################################
####### NORMAL FUND TRANSFER SEND ######
########################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransfersendnormal(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate,defaultbank='Y')
                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)

                clcash = allcash[0].clcash
                clbank = allbank[0].clbank                


                ffundtype = 'Normal Fund Transfer'
                transferto = Locationlogin.objects.values('locationcode','locationname').filter(~Q(locationcode=loginlocationcode)).distinct().order_by('locationname')                 
 
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'allbank':allbank,
                        'clcash':clcash,
                        'clbank':clbank,
                        'ffundtype':ffundtype,
                        'transferto':transferto,
                          }

                if request.method == "POST" and request.POST.get('checkbox') is not None:

                        ffundtype = request.POST.get('fundtype')
                        famount = request.POST.get('amount')
                        ftransferto = request.POST.get('transferto')
                        fpaymode = request.POST.get('paymode')
                        fappbankac = request.POST.get('appbankac')
                        fcheckbox = request.POST.get('checkbox')


                        flocationcode = loginlocationcode
                        flocationname = loginlocationname


                        trans = Transcd.objects.get(transcd=ftransferto)
                        ftrans = trans.id    
                        ftranstocd = trans.transcd
                        ftranstonm = trans.transnm          

                        ffundtype = 'Normal Fund Transfer'
                        if ffundtype == 'Normal Fund Transfer':
                            ftranscd = '3375'
                            ftransnm = 'NORMAL FUND TRANSFER'



                        if fpaymode=="BANK": 
                            allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                            fclbank = allbank.clbank
                            fbankac = allbank.bankac
                            fbankcode = allbank.bankcode
                            fbankname = allbank.bankname

                            if fclbank < int(famount):
                                 message = "Not sufficient Fund in Bank to SEND " + ftranstonm + " / Rs. " +famount 

                                 messages.success(request, message)
                                 return HttpResponseRedirect('/fundtransfersendnormal/')

                        if fpaymode=="CASH":
                             allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                             fclcash = allcash[0].clcash

                             if fclcash < int(famount):
                                 message = "Not sufficient Fund in Cash to SEND " + ftranstonm + " / Rs. " + famount

                                 messages.success(request, message)
                                 return HttpResponseRedirect('/fundtransfersendnormal/')

                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()


                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)            
   
                        if fpaymode == "BANK" and fclbank > int(famount):
                            
                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fappbankac,date=loginrundate)
                                fclbank = allbank.clbank
                                fbankac = allbank.bankac
                                fbankcode = allbank.bankcode
                                fbankname = allbank.bankname
                     
                                fnarr = "FUND SEND/"+ffundtype.strip()+"/Rs."+famount.strip()+" Through"+fpaymode

                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                                opclid = allbank.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranstocd,transnm=ftranstonm,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="D", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                trans = Transcd.objects.get(transcd=fbankcode)
                                ftrans = trans.id    

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=fbankcode,transnm=fbankname,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                allbank.clbank = allbank.clbank - int(famount)
                                allbank.save()

                        if fpaymode=="CASH" and  fclcash > int(famount):
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                                fclcash = allcash[0].clcash
                    
                                fnarr = "FUND SEND/"+ffundtype.strip()+"/Rs."+famount.strip()+" Through "+fpaymode         

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranstocd,transnm=ftranstonm,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="D", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()
            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                                for all in allcash:
                                    all.clcash = all.clcash - int(famount)
                                    all.save()


                        trans = Fundsendreceive(locationcode=loginlocationcode,
                               locationname=loginlocationname,
                               date=loginrundate,transid=ftransid,
                               translocationcode=ftranstocd, translocationname=ftranstonm,
                               mode=fpaymode,
                               transcd=ftranscd,
                               transnm=ftransnm,
                               fundtype=ffundtype,amount=famount,drcr="D",
                               status = 'A')
            
                        trans.save()

                        message = "Normal Fund Send to " + ftranstonm + " / Rs. " + famount + " / " + \
                            "Through " + fpaymode + " Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundtransfersendnormal/')


                else:
                        return render(request, 'admssapp/fundtransfersendnormal.html' , context)



###########################################
####### NORMAL FUND TRANSFER RECEIVE ######
###########################################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransferreceivenormal(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 

                fndrec = Fundsendreceive.objects.filter(translocationcode=loginlocationcode,status='A',transcd__in=['3375'])
                allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode, date=loginrundate)

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'fndrec':fndrec,
                          }

                if request.method == "POST":

                        ffundrec = request.POST.get('transferreceive')

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        fndrec = Fundsendreceive.objects.get(transid=ffundrec, status='A')

                        ffundtype = fndrec.fundtype
                        flocationname = fndrec.locationname
                        famount = fndrec.amount
                        fmode = fndrec.mode
                        fdate = fndrec.date
                        ftransid = fndrec.transid
  
                        context={'loginlocationcode': loginlocationcode,
                                 'loginlocationname': loginlocationname,
                                 'loginrundate': loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate': currdate,
                                 'ffundtype': ffundtype,
                                 'flocationname': flocationname,
                                 'famount': famount,
                                 'fmode': fmode,
                                 'fdate': fdate,
                                 'ftransid': ftransid,
                                 'allbank': allbank,
                                   }

                        return render(request, 'admssapp/fundtransferreceivegetnormal.html', context)

                else:
                        return render(request, 'admssapp/fundtransferreceivenormal.html' , context)



##################################################
####### NORMAL FUND TRANSFER RECEIVE COMMIT ######
##################################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransferreceivecommitnormal(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
 
 
                if request.method == "POST":

                        ffundrec = request.POST.get('transferreceive')
                        fpaymode = request.POST.get('mode')
                        fbankac = request.POST.get('bankac')
                        fbankchq = request.POST.get('bankchq')

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname

                        fndrec = Fundsendreceive.objects.get(transid=ffundrec, status='A')

                        ffundtype = fndrec.fundtype
                        flocationname = fndrec.locationname
                        flocationcode = fndrec.locationcode

                        famount = fndrec.amount
                        fpaymode = fndrec.mode
                        fdate = fndrec.date
                        ftransid = fndrec.transid
                        ftranscd = fndrec.locationcode
                        ftransnm = fndrec.locationname

                        
                        alllocmast = Locationlogin.objects.get(locationcode=loginlocationcode,user_id=loguserid)
                        mtransidnum = alllocmast.transidnum + 1
                        alllocmast.transidnum = alllocmast.transidnum + 1
                        alllocmast.save()

                        yy = loginrundate.strftime("%Y")
                        yy = yy[0:2]
                        mm = loginrundate.strftime("%m")
                        dd = loginrundate.strftime("%d")
                    
                        ftransid = loginlocationcode+yy+mm+dd+str(mtransidnum).zfill(4)    

                        transcd = Transcd.objects.get(transcd=flocationcode)
                        ftrans = transcd.id   


                        if fpaymode == "BANK":
                            
                                allbank = Opclcashbank.objects.get(locationcode=loginlocationcode,bankac=fbankac,date=loginrundate)
                                fclbank = allbank.clbank
                                fbankac = allbank.bankac
                                fbankcode = allbank.bankcode
                                fbankname = allbank.bankname
                     
                                fnarr = "FUND RECEIVED/"+ffundtype.strip()+"/Rs."+str(famount).strip()+" Through"+fpaymode

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    chequeno=fbankchq,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                trans = Transcd.objects.get(transcd=fbankcode)
                                ftrans = trans.id    


                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=fbankcode,transnm=fbankname,
                                    bankac=fbankac,
                                    mode=fpaymode,
                                    chequeno=fbankchq,                                    
                                    narration=fnarr,amount=famount,drcr="D", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()

                                allbank.clbank = allbank.clbank + int(famount)
                                allbank.save()

                        if fpaymode=="CASH" :
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
                                fclcash = allcash[0].clcash
                    
                                fnarr = "FUND SEND/"+ffundtype.strip()+"/Rs."+str(famount).strip()+" Through "+fpaymode         

                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate).first()
                                opclid = allcash.id

                                db = Daybook(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    date=loginrundate,transid=ftransid,
                                    transcd=ftranscd,transnm=ftransnm,
                                    mode=fpaymode,
                                    narration=fnarr,amount=famount,drcr="C", trans_id = ftrans,
                                    clcashbank_id = opclid)
            
                                db.save()
            
                                allcash = Opclcashbank.objects.filter(locationcode=loginlocationcode,date=loginrundate)
        
                                for all in allcash:
                                    all.clcash = all.clcash + int(famount)
                                    all.save()

                        
                        fndrec.transtransid = ftransid
                        fndrec.transdate = loginrundate
                        fndrec.status = 'C'

                        fndrec.save()

                        message = "FUND RECEIVED From " + flocationname + " / Rs. " + str(famount) + " / " +  "Through " + fpaymode + " Processed Succesfully"

                        messages.success(request, message)
                        return HttpResponseRedirect('/fundtransferreceivenormal/')

                        return render(request, 'admssapp/fundtransferreceiveget.html', context)
                else:
                        return render(request, 'admssapp/fundtransferreceive.html' , context)







################################################
####### FUND TRANSFER SEND RECEIVE REPORT ######
################################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def fundtransfersendreceivereport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                alldata = Fundsendreceive.objects.filter(Q(locationcode=loginlocationcode) | Q(translocationcode=loginlocationcode)).first()
                first = Fundsendreceive.objects.filter(Q(locationcode=loginlocationcode) | Q(translocationcode=loginlocationcode)).order_by('id')[0]
                last = Fundsendreceive.objects.filter(Q(locationcode=loginlocationcode) | Q(translocationcode=loginlocationcode)).order_by('-id')[0]

                
                ffromdate = first.date
                ftodate = last.date

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'ffromdate': ffromdate,
                        'ftodate':ftodate,
                          }

                if request.method == "POST":

                        ffromdate = request.POST.get('fromdate')
                        ftodate = request.POST.get('todate')


                        alldata = Fundsendreceive.objects.filter(Q(locationcode=loginlocationcode) | Q(translocationcode=loginlocationcode),date__gte=ffromdate,date__lte=ftodate).order_by('id')

                        allsumm = Fundsendreceive.objects.filter(Q(locationcode=loginlocationcode) | Q(translocationcode=loginlocationcode),date__gte=ffromdate,date__lte=ftodate).aggregate(totac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                        totalid = allsumm.get('totac')
                        totalamt = allsumm.get('totamt')

                        context={'loginlocationcode':loginlocationcode,
                                'loginlocationname':loginlocationname,
                                 'loginrundate':loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate':currdate,
                                 'ffromdate':ffromdate,
                                 'ftodate':ftodate,
                                 'alldata':alldata,
                                 'totalamt': totalamt,
                                   }

                        return render(request, 'admssapp/fundsendreceivereportshow.html' , context)                    

                else:
                    return render(request, 'admssapp/fundsendreceivereport.html', context)


################################
####### WHATSAPP DAY DATA ######
################################
@login_required(login_url='login')
@csrf_exempt
@never_cache

def whatsappdaydata(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                fdataday = loginrundate.strftime("%Y-%m-%d")

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'fdataday':fdataday,
                          }

                if request.method == "POST":
                    datatype = request.POST.get('datatype')
                    dataday = request.POST.get('dataday')

                    dataday = datetime.strptime(dataday, "%Y-%m-%d").date()


                    #ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                    #ftodate = ffromdate + timedelta(days=5)
             
                    ffromdate = dataday - timedelta(days=dataday.weekday())
                    ftodate = ffromdate + timedelta(days=5)



                    if datatype == 'Today Fresh Message':

                        #todayday = calendar.day_name[date.today().weekday()]
                        todayday = calendar.day_name[dataday.weekday()]     

                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(colldaychar=todayday) & Q(applastemidepdate__lt=ffromdate) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY')).only('loanid', 'appname', 'apploanemi', 'colldaynum', 'colldaychar', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode', 'appname')
                        daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(colldaychar=todayday) & Q(appemifreq='WEEKLY')).aggregate(totac=Coalesce(Count('loanid'), 0))

                        #daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(colldaychar=todayday) & Q(applastemidepdate__lt=ffromdate) & ~Q(applastemidepdate=None) & ~Q(loanid__in=['I100100000658','I100100000653','I100100000654','I100100000601','I100100000494','I100100000593','I100100000625']) & Q(appemifreq='WEEKLY')).only('loanid', 'appname', 'apploanemi', 'colldaynum', 'colldaychar', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode', 'appname')
                        #daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(colldaychar=todayday) & Q(appemifreq='WEEKLY')).aggregate(totac=Coalesce(Count('loanid'), 0))
                    
                        totrec = daydatasumm.get("totac")
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(calendar.day_name[dataday.weekday()])
                        writer = csv.writer(response)
                        writer.writerow(['loanid', 'appname','apploanemi', 'colldaynum', 'colldaychar','applastemidepdate','appmobileno','coappmobileno','adminpersonname','rpersonname'])

                        for user in daydata:
                            writer.writerow([user.loanid, user.appname,user.apploanemi, user.colldaynum,user.colldaychar,user.applastemidepdate,user.appmobileno,user.coappmobileno,user.adminpersonname,user.rpersonname])

                        return response


                    if datatype == 'Current Week reminder Message' :


                        todaydaychar = calendar.day_name[loginrundate.weekday()]
                        todaydaynum = loginrundate.weekday() + 1


                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum)).only('loanid', 'appname', 'apploanemi', 'colldaychar', 'colldaynum', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode','colldaynum')
                        daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum)).aggregate(totac=Coalesce(Count('loanid'), 0))
                        

                        #daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum) & ~Q(loanid__in=['I100100000658','I100100000653','I100100000654','I100100000601','I100100000494','I100100000593','I100100000625'])).only('loanid', 'appname', 'apploanemi', 'colldaychar', 'colldaynum', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode','colldaynum')
                        #daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum)).aggregate(totac=Coalesce(Count('loanid'), 0))
                        

                        totrec = daydatasumm.get("totac")
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('weekpending')
                        writer = csv.writer(response)
                        writer.writerow(['loanid', 'appname', 'apploanemi', 'colldaynum',
                                        'colldaychar', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname'])

                        for user in daydata:
                            writer.writerow([user.loanid, user.appname, user.apploanemi, user.colldaynum,
                                            user.colldaychar, user.applastemidepdate, user.appmobileno, user.coappmobileno,user.adminpersonname,user.rpersonname])

                        return response

                    if datatype == 'LastWeek reminder Message' :

                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A'))
                            
                        for data in daydata:

                                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=data.loanid)
                                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=data.loanid).order_by('date','id')
                                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=data.loanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                                    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=data.loanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

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
                                
                                    fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                                    foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                                    ftotaldueamt = fcurrdueamt + foverdueamt - flatefees + latefee
                                    fcurrdueamt = fcurrdueamt + latefee
                                    fapptotalbalamt = fapptotalbalamt + latefee
                                    
                                    if ftotaldueamt < fcurrdueamt:
                                       ftotaldueamt = fcurrdueamt
                                       if fcurrdueamt < fapptotalbalamt:
                                           ftotaldueamt = fapptotalbalamt
                                    
                                    loanmast.instoverdueamttmp = ftotaldueamt
                                    loanmast.instoverduetmp = fcurremibal
                                    loanmast.save()





                        #ffromdate = loginrundate - (timedelta(days=5) + timedelta(days=loginrundate.weekday()))
                        idx = (loginrundate.weekday() + 1) % 7
                        lastsunday = (loginrundate - timedelta(7 + idx - 1))


                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=lastsunday) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY')).only('loanid', 'appname', 'apploanemi', 'colldaychar', 'colldaynum', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode','colldaynum')

                        #response = HttpResponse(content_type='text/csv')
                        #response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('lastweekpending')
                        #writer = csv.writer(response)
                        #writer.writerow(['loanid', 'appname','apploanemi', 'colldaynum', 'colldaychar','applastemidepdate','instoverdue','instoverdueamt','instoverduetmp','instoverdueamttmp','appmobileno','coappmobileno','guarname','guarmobileno','adminpersonname','rpersonname'])

                        #for user in daydata:
                        #    writer.writerow([user.loanid, user.appname, user.apploanemi, user.colldaynum, user.colldaychar,
                        #                    user.applastemidepdate,user.instoverdue,user.instoverdueamt, user.instoverduetmp,user.instoverdueamttmp,user.appmobileno, user.coappmobileno, user.guarname, user.guarmobileno,user.adminpersonname,user.rpersonname])


                        #return response



                        from django.http import StreamingHttpResponse
                        import itertools



                        class Echo:
                            def write(self, value):
                                return value

                        rows = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=lastsunday) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY')).values_list('loanid', 'appname','apploanemi', 'colldaynum', 'colldaychar','applastemidepdate','instoverdue','instoverdueamt','instoverduetmp','instoverdueamttmp','appmobileno','coappmobileno','guarname','guarmobileno','adminpersonname','rpersonname')
                        headers = [("loanid","appname","apploanemi","colldaynum","colldaychar","applastemidepdate","instoverdue","instoverdueamt","instoverduetmp","instoverdueamttmp","appmobileno","coappmobileno","guarname","guarmobileno","adminpersonname","rpersonname")]
                        echo_buffer = Echo()
                        csv_writer = csv.writer(echo_buffer)
                        rows = itertools.chain(headers, rows)

                        def iter_content(rows, headers):
                            pseudo_buffer = Echo()
                            writer = csv.writer(pseudo_buffer)
                            #yield pseudo_buffer.write(headers)
                            for row in rows:
                                yield writer.writerow(row)


                        response = StreamingHttpResponse((iter_content(rows, headers)),status=200,content_type="text/csv",)
                        response["Content-Disposition"] = 'attachment; filename="lastweekpending.csv"'
                        return response




                    if datatype == 'Overdue beyond week Message':

                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A'))
                            
                        for data in daydata:

                                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=data.loanid)
                                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=data.loanid).order_by('date','id')
                                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=data.loanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))
                                    loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=data.loanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

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
                                
                                    fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                                    foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                                    ftotaldueamt = fcurrdueamt + foverdueamt - flatefees + latefee
                                    fcurrdueamt = fcurrdueamt + latefee
                                    fapptotalbalamt = fapptotalbalamt + latefee
                                    
                                    if ftotaldueamt < fcurrdueamt:
                                       ftotaldueamt = fcurrdueamt
                                       if fcurrdueamt < fapptotalbalamt:
                                           ftotaldueamt = fapptotalbalamt
                                    
                                    loanmast.instoverdueamttmp = ftotaldueamt
                                    loanmast.instoverduetmp = fcurremibal
                                    loanmast.save()



                        daydata =  Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',instoverdue__gte=2).order_by("-instoverdue")
                        emiduesumm =  Loanmaster.objects.filter(locationcode=loginlocationcode,status='A',instoverdue__gte=2).aggregate(totac=Count("loanid"), totdueamt=Sum("instoverdueamt"),)


                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="overdue.csv"'
                        writer = csv.writer(response)
                        writer.writerow(['loanid', 'appname','apploanemi', 'colldaynum', 'colldaychar','applastemidepdate','instoverdue','instoverdueamt','instoverduetmp','instoverdueamttmp','appmobileno','coappmobileno','guarname','guarmobileno','adminpersonname','rpersonname'])

                        for user in daydata:
                            writer.writerow([user.loanid, user.appname, user.apploanemi, user.colldaynum, user.colldaychar,
                                            user.applastemidepdate,user.instoverdue,user.instoverdueamt, user.instoverduetmp,user.instoverdueamttmp,user.appmobileno, user.coappmobileno, user.guarname, user.guarmobileno,user.adminpersonname,user.rpersonname])

                        return response


                        last_14_days = loginrundate - timedelta(days=14)
                        daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(applastemidepdate__lte=last_14_days) & Q(
                            appemiduedate__lt=last_14_days) & Q(status="A")).order_by('applastemidepdate')

                        daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(applastemidepdate__lte=last_14_days) & Q(
                            appemiduedate__lt=last_14_days) & Q(status="A")).order_by('applastemidepdate').aggregate(totac=Coalesce(Count('loanid'), 0))
                        totrec = daydatasumm.get("totac")

                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="overdue.csv"'
                        writer = csv.writer(response)
                        writer.writerow(['loanid', 'appname','apploanemi', 'colldaynum', 'colldaychar','applastemidepdate','appmobileno','coappmobileno','guarname','guarmobileno','admin'])

                        for user in daydata:
                            writer.writerow([user.loanid, user.appname, user.apploanemi, user.colldaynum, user.colldaychar,
                                            user.applastemidepdate, user.appmobileno, user.coappmobileno, user.guarname, user.guarmobileno,user.admin])

                        return response

                    if datatype == 'Greetings' :


                        
                        todaydaychar = calendar.day_name[loginrundate.weekday()]
                        todaydaynum = loginrundate.weekday() + 1

      
                        #daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode))

                        daydata = Loanmaster.objects.all().distinct('appname').order_by('appname')
                        daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode)).aggregate(totac=Coalesce(Count('loanid'), 0))
                        

                        #daydata = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & ~Q(applastemidepdate=None) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum) & ~Q(loanid__in=['I100100000658','I100100000653','I100100000654','I100100000601','I100100000494','I100100000593','I100100000625'])).only('loanid', 'appname', 'apploanemi', 'colldaychar', 'colldaynum', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname').order_by('adminpersoncode','colldaynum')
                        #daydatasumm = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(status='A') & Q(applastemidepdate__lt=ffromdate) & Q(appemifreq='WEEKLY') & Q(colldaynum__lt=todaydaynum)).aggregate(totac=Coalesce(Count('loanid'), 0))

                        totrec = daydatasumm.get("totac")
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('greetings')
                        writer = csv.writer(response)
                        writer.writerow(['loanid', 'appname', 'apploanemi', 'colldaynum',
                                        'colldaychar', 'applastemidepdate', 'appmobileno', 'coappmobileno','adminpersonname','rpersonname'])

                        for user in daydata:
                            writer.writerow([user.loanid, user.appname, user.apploanemi, user.colldaynum,
                                            user.colldaychar, user.applastemidepdate, user.appmobileno, user.coappmobileno,user.adminpersonname,user.rpersonname])

                        return response
         
                return render(request, 'admssapp/whatsappdaydata.html' , context)     




def whatsappmessage(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

            nname = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').order_by('appname','apploandate')
            context={'loginlocationcode':loginlocationcode,
                     'loginlocationname':loginlocationname,
                     'loginrundate':loginrundate,
                     'loginstatus':loginstatus,
                     'currdate': currdate,
                     'nname':nname,
                        }
            
            if request.method == "POST":

                fapploanid = request.POST.get('loanidname')
                fmessagetype = request.POST.get('messagetype')
                if fmessagetype == 'BORROWER':
                    fmessagetypedisplay = 'Message to Borrower'
                    ftextmessage = "आज आपकी लोन की किश्त का भुगतान करने का दिन है, आज ही कृपया लोन की किश्त का भुगतान करे और CIBIL (सीबिल) पर नकारात्मक प्रभाव एवं विलम्ब शुल्क से बचे | यदि अपने लोन किश्त का भुगतान कर दिया है तो इस मेसेज को इगनोर करे | धन्यवाद                                                                       एड्मास माइक्रो फाइनेंस"
                elif fmessagetype == 'COBORROWER':
                    ftextmessage = ""
                    fmessagetypedisplay = 'Message to Co-Borrower'
                elif fmessagetype == 'GUARANTOR':
                    ftextmessage = ""
                    fmessagetypedisplay = 'Message to Guarantor'

                loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)
                fapploanid = loanmast.loanid
                fappname = loanmast.appname
                fappmobileno = loanmast.appmobileno
                fcoappmobileno = loanmast.coappmobileno
                fguarmobileno = loanmast.guarmobileno
                fappshoplocation = loanmast.appshoplocation
                


                context={'loginlocationcode':loginlocationcode,
                     'loginlocationname':loginlocationname,
                     'loginrundate':loginrundate,
                     'loginstatus':loginstatus,
                     'currdate': currdate,
                     'nname':nname,
                     'fapploanid':fapploanid,
                     'fappname':fappname,
                     'fmessagetype':fmessagetype,
                     'fmessagetypedisplay':fmessagetypedisplay,
                     'fappshoplocation':fappshoplocation,
                     'ftextmessage':ftextmessage,

                        }


                return render(request, 'admssapp/whatsappsmessageget.html', context)

            return render(request, 'admssapp/whatsappsmessage.html', context)


def whatsappmessageget(request):

        loguserid = request.session['loguserid']
        ll = Locationlogin.objects.get(user=loguserid)

        loginlocationcode = ll.locationcode
        loginlocationname = ll.locationname
        loginrundate = ll.rundate
        loginstatus = ll.status
        currdate = date.today()

        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in (['B', 'A']):
            return HttpResponseRedirect('/login')
        else:

            if request.method == "POST":

                fapploanid = request.POST.get('loanidname')
                fmessagetype = request.POST.get('messagetype')
                Message = request.POST.get('textmessage')   
                loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)    
                fapploanid = loanmast.loanid
                fappname = loanmast.appname
                fappmobileno = loanmast.appmobileno
                fcoappmobileno = loanmast.coappmobileno
                fguarmobileno = loanmast.guarmobileno
                fappshoplocation = loanmast.appshoplocation
                
                if fmessagetype == 'BORROWER':
                    Ph = loanmast.appmobileno
                elif fmessagetype == 'COBORROWER':
                    Ph = loanmast.coappmobileno
                elif fmessagetype == 'GUARANTOR':
                    fmessagetypedisplay = 'Message to Guarantor'
                    Ph = loanmast.guarmobileno



        #        def Whatsappsendmessage(Ph,Message):
        #            import os
        #            os.environ['DISPLAY'] = ':0'
        #            #import time
        #            #import webbrowser 
        #            #import Xlib.display
        #            #from pyvirtualdisplay.display import Display
        #            #disp = Display(visible=True, size=(1366, 768), backend="xvfb", use_xauth=True)
        #            #disp.start()
        #            #import pyautogui
        #            #pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
        #
        #            #Phone = "+91"+Ph
        #            #webbrowser.open_new_tab('https://web.whatsapp.com/send?phone=' + Phone+'&test='+Message)
        #            #time.sleep(30)
        #            #pyautogui.press('enter')
        #
        #            import time
        #            import webbrowser as web
        #            from datetime import datetime
        #            from re import fullmatch
        #            from urllib.parse import quote
        #            import pyautogui as pg
        #            #from selenium.webdriver.common.action_chains import ActionChains

        #            from pywhatkit.core import core, exceptions, log    

        #            pg.FAILSAFE = False

        #            core.check_connection()

        #            phone_no = '+919005575276'
        #            message = 'Test Message'


        #            web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}", 2)
        #            time.sleep(4)
        #            pg.click(core.WIDTH / 2, core.HEIGHT / 2)
        #            pg.click('enter')
        #            time.sleep(4)


                
        #        Whatsappsendmessage(Ph,Message) 

        #        message = "Whatsapp Message send to" + fappname + " on mobile no. " + Ph+ " send Succesfully"

        #        messages.success(request, message)
        #        return HttpResponseRedirect('/whatsappmessage/')




        import sys
        import time
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from selenium.common.exceptions import NoSuchElementException

        options = webdriver.ChromeOptions()
        options.add_argument(r'--user-data-dir=C:\\whatsappsms\Default')
        options.add_argument('--profile-directory=Default')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.headless = True

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.get("https://web.whatsapp.com")
        wait = WebDriverWait(driver, 100)


        #message = 'आज आपकी लोन की किश्त का भुगतान करने का दिन है, आज ही कृपया लोन की किश्त का भुगतान करे और CIBIL (सीबिल) पर नकारात्मक प्रभाव एवं विलम्ब शुल्क से बचे | यदि अपने लोन किश्त का भुगतान कर दिया है तो इस मेसेज को इगनोर करे | धन्यवाद                                                                             एड्मास माइक्रो फाइनेंस'
        message = 'वर्तमान सप्ताह में आपकी लोन की किश्त का भुगतान करने का दिन निकल चुका है, आज ही कृपया लोन की किश्त का भुगतान करे और CIBIL (सीबिल) पर नकारात्मक प्रभाव से बचे | यदि अपने लोन किश्त का भुगतान कर दिया है तो इस मेसेज को इगनोर करे | धन्यवाद                                                                         एड्मास माइक्रो फाइनेंस'
        contact = fappmobileno



        search_box = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')))
        search_box.clear()

        search_box.send_keys(contact)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)


        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id = "pane-side"]/div[1]/div/div/div[11]/div')))
            send_message = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '// *[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]')))
            send_message.send_keys(message)
            send_message.send_keys(Keys.ENTER)


            send.append(name + '/' + contact)
        except:
            notsend.append(name + '/' + contact)



        time.sleep(5)
        driver.close()




#############################
####### NEW LOAN LEADS ######
#############################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadnew(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 
                todaymonth = loginrundate.month
                todayyear = loginrundate.year

                monthyear = str(loginrundate.year)


                todaymonthchar = calendar.month_name[todaymonth] +"'"+monthyear

                Loanleadsumm.objects.filter(locationcode=loginlocationcode).delete()
                allperson = Personmaster.objects.filter(locationcode=loginlocationcode,admin='Y').distinct('personname')
                allfi = Loanlead.objects.filter(locationcode=loginlocationcode,loandisb='N').order_by('id')
                summallfi = Loanlead.objects.filter(locationcode=loginlocationcode,status='A').values('leadpersonname').annotate(totfi=Coalesce(Count('leadpersonname'),0))    
             

                nooffi = 0
                for all in allperson:
                    ffipersoncode = all.personcode
                    ffipersonname = all.personname

                    summfi1 = Loanlead.objects.filter(locationcode=loginlocationcode,leadpersoncode=ffipersoncode).aggregate(totfi=Coalesce(Count('leadpersoncode'),0))
                    summfi2 = Loanlead.objects.filter(locationcode=loginlocationcode, secondpersoncode=ffipersoncode).aggregate(totfi=Coalesce(Count('secondpersoncode'), 0))
                    summdisb1 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) &  Q(leadpersoncode=ffipersoncode)).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0))
                    summdisb2 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) &  Q(secondpersoncode=ffipersoncode)).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus2', filter= Q(status='A') & Q(fistatus1='N')), 0))

                    #summdisb = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(leadpersoncode=ffipersoncode) | Q(secondpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0),active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0)
                    #aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

                 

                    loanleaddb = Loanleadsumm(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    personcode=ffipersoncode,
                                    personname=ffipersonname,
                                    leads = summfi1.get("totfi") + summfi2.get("totfi"),
                                    disb = summdisb1.get("disb"),
                                    rejected=summdisb1.get("rejected"),
                                    active=summdisb1.get("active") + summdisb2.get("active"),
                                    datarange='TOTAL')
                    loanleaddb.save()     


                todaymonth = loginrundate.month
                todayyear = loginrundate.year


                nooffi = 0
                for all in allperson:
                    ffipersoncode = all.personcode
                    ffipersonname = all.personname

                    summfi1 = Loanlead.objects.filter(locationcode=loginlocationcode,leadpersoncode=ffipersoncode,leaddate__year=todayyear,leaddate__month=todaymonth).aggregate(totfi=Coalesce(Count('leadpersoncode'),0))
                    summfi2 = Loanlead.objects.filter(locationcode=loginlocationcode, secondpersoncode=ffipersoncode,leaddate__year=todayyear,leaddate__month=todaymonth).aggregate(totfi=Coalesce(Count('secondpersoncode'), 0))
                    summdisb1 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) &  Q(leadpersoncode=ffipersoncode) &  Q(leaddate__year=todayyear) & Q(leaddate__month=todaymonth)).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0))
                    summdisb2 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) &  Q(secondpersoncode=ffipersoncode) &  Q(leaddate__year=todayyear) & Q(leaddate__month=todaymonth)).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus2', filter= Q(status='A') & Q(fistatus1='N')), 0))

                    #summdisb1 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(leadpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0))
                    #summdisb2 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(secondpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus2', filter= Q(status='A') & Q(fistatus1='N')), 0))

                    #summdisb = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(leadpersoncode=ffipersoncode) | Q(secondpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0),active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0)
                    #aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))


                    loanleaddb = Loanleadsumm(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    personcode=ffipersoncode,
                                    personname=ffipersonname,
                                    leads = summfi1.get("totfi") + summfi2.get("totfi"),
                                    disb = summdisb1.get("disb"),
                                    rejected=summdisb1.get("rejected"),
                                    active=summdisb1.get("active") + summdisb2.get("active"),
                                    datarange = 'MONTH')
                    loanleaddb.save()  

                leadsumm = Loanleadsumm.objects.filter(locationcode=loginlocationcode,datarange='TOTAL').order_by('personname')
                leadsummmonth = Loanleadsumm.objects.filter(locationcode=loginlocationcode,datarange='MONTH').order_by('personname')

                allfilist = Loanlead.objects.filter(locationcode=loginlocationcode,status='C').order_by('id')
                monthfilist = Loanlead.objects.filter(locationcode=loginlocationcode,leaddate__month=loginrundate.month,leaddate__year=loginrundate.year,status='C').order_by('id')
                month = loginrundate.strftime("%B")+"'"+str(loginrundate.year)
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'allperson':allperson,
                        'allfi':allfi,
                        'summallfi':summallfi,
                        'leadsumm':leadsumm,
                        'todaymonthchar':todaymonthchar,
                        'leadsummmonth':leadsummmonth,
                        'allfilist':allfilist,
                        'monthfilist':monthfilist,
                        'month':month,
                          }

                if request.method == "POST":

                        fappname = request.POST.get('appname')
                        fappmobileno = request.POST.get('appmobileno')


                        allloan = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(appmobileno=fappmobileno) | Q(appname__contains=fappname)).order_by('id')
                        alllead = Loanlead.objects.filter(Q(locationcode=loginlocationcode) & Q(appmobileno=fappmobileno) | Q(appname__contains=fappname) & Q(status='A')).select_related('loanmaster')

                        #User.objects.filter(~Exists(Reports.objects.filter(user__eq=OuterRef('pk')))


                        context={'loginlocationcode':loginlocationcode,
                                 'loginlocationname':loginlocationname,
                                 'loginrundate':loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate': currdate,
                                 'allloan':allloan,
                                 'alllead':alllead,
                                 'fappname':fappname,
                                 'fappmobileno':fappmobileno,

                                 }

                        return render(request, 'admssapp/loanleadnewget.html', context)


                else:
                    return render(request, 'admssapp/loanleadnew.html', context)


#################################
####### NEW LOAN LEADS GET ######
#################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadnewget(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:

                if request.method == "POST":

                        fappname = request.POST.get('appname')
                        fappmobileno = request.POST.get('appmobileno')
                        allperson = Personmaster.objects.filter(locationcode=loginlocationcode,admin='Y').distinct('personname')
                        fdate = loginrundate.strftime("%Y-%m-%d")

                        context= {'loginlocationcode':loginlocationcode,
                                 'loginlocationname':loginlocationname,
                                 'loginrundate':loginrundate,
                                 'loginstatus':loginstatus,
                                 'currdate': currdate,
                                 'fappname':fappname,
                                 'fappmobileno':fappmobileno,
                                 'allperson':allperson,
                                 'fdate':fdate,
                                 }
                        return render(request, 'admssapp/loanleadnewcommit.html', context)
                else:
        
                        return render(request, 'admssapp/loanleadnewget.html', context)


####################################
####### NEW LOAN LEADS COMMIT ######
####################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadnewcommit(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   
 

                if request.method == "POST":

                        fappname = request.POST.get('appname')
                        fappgender = request.POST.get('appgender')
                        fappdob = request.POST.get('appdob')
                        fappmaritalstatus = request.POST.get('appmaritalstatus')
                        fappmobileno = request.POST.get('appmobileno')
                        fappbusiness = request.POST.get('appbusiness')
                        fappshoplocation = request.POST.get('appshoplocation')
                        fleadperson = request.POST.get('leadperson')
                        fsecondperson = request.POST.get('secondperson')
                        ftodaydate = request.POST.get('todaydate')


                        leadperson = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fleadperson)
                        secondperson = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fsecondperson)

                        fleadpersoncode = leadperson.personcode
                        fleadpersonname = leadperson.personname

                        fsecondpersoncode = secondperson.personcode
                        fsecondpersonname = secondperson.personname


                        loanleaddb = Loanlead(locationcode=loginlocationcode,
                                    locationname=loginlocationname,
                                    appname=fappname,
                                    appgender=fappgender,
                                    appmaritalstatus=fappmaritalstatus,
                                    appmobileno=fappmobileno,
                                    appbusiness=fappbusiness,
                                    appshoplocation=fappshoplocation,
                                    leadpersoncode=fleadpersoncode,
                                    leadpersonname=fleadpersonname,
                                    secondpersoncode=fsecondpersoncode,
                                    secondpersonname=fsecondpersonname,
                                    leaddate=ftodaydate,
                                    status='A',
                                    fistatus1='N',
                                    fistatus2='N',
                                    loandisb='N',
                                       )
            
                        loanleaddb.save()

                        message = "Loan Lead " + fappname +' / '+fappmobileno+' / '+fappbusiness+ " Generated successfully..."

                        messages.success(request, message)
                        return HttpResponseRedirect('/loanleadnew/')

                else:
                    return render(request, 'admssapp/loanleadnew.html', context)



#################################
######## LOAN LEAD UPDATE  ######
#################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadupdate(request,loanlead_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:


            loanlead = Loanlead.objects.get(id=loanlead_id)

            floanlead = loanlead_id
            fappname=loanlead.appname
            fappmaritalstatus=loanlead.appmaritalstatus
            fappgender=loanlead.appgender
            fappmobileno=loanlead.appmobileno
            fappshoplocation=loanlead.appshoplocation
            fappbusiness=loanlead.appbusiness
            fleaddate=loanlead.leaddate
            fleadpersoncode=loanlead.leadpersoncode
            fleadpersonname=loanlead.leadpersonname
            fsecondpersoncode=loanlead.secondpersoncode
            fsecondpersonname=loanlead.secondpersonname
            fstatus=loanlead.status
            ffidate1=loanlead.fidate1
            ffidate2=loanlead.fidate2
            ffistatus1=loanlead.fistatus1
            ffistatus2=loanlead.fistatus2

        
            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'fappname':fappname,
                    'fappmaritalstatus':fappmaritalstatus,
                    'fappgender':fappgender,
                    'fappmobileno':fappmobileno,
                    'fappshoplocation':fappshoplocation,
                    'fappbusiness':fappbusiness,
                    'fleaddate':fleaddate,
                    'fleadpersonname':fleadpersonname,
                    'fsecondpersonname':fsecondpersonname,
                    'floanlead':floanlead,
                    'ffidate1':ffidate1,
                    'ffidate2':ffidate2,
                    'ffistatus1':ffistatus1,
                    'ffistatus2':ffistatus2,
                    }


            if loanlead==None:
                pass
            else:
                return render(request,"admssapp/loanleadupdate.html", context)




#####################################
######## LOAN LEAD UPDATE GET  ######
#####################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadupdateget(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:


            updatefi1 = request.POST.get('updatefi1')
            updatefi2 = request.POST.get('updatefi2')
            disburse = request.POST.get('disburse')
            changeperson = request.POST.get('changeperson')
            deleteentry = request.POST.get('deleteentry')
            
            floanleadid = int(request.POST.get('loanleadid'))


            loanlead = Loanlead.objects.get(id=floanleadid)

            fappname=loanlead.appname
            fappmaritalstatus=loanlead.appmaritalstatus
            fappgender=loanlead.appgender
            fappmobileno=loanlead.appmobileno
            fappshoplocation=loanlead.appshoplocation
            fappbusiness=loanlead.appbusiness
            fleaddate=loanlead.leaddate
            fleadpersoncode=loanlead.leadpersoncode
            fleadpersonname=loanlead.leadpersonname
            fsecondpersoncode=loanlead.secondpersoncode
            fsecondpersonname=loanlead.secondpersonname
            fstatus=loanlead.status
            ffidate1=loanlead.fidate1
            ffidate2=loanlead.fidate2

            fistatus1=loanlead.fistatus1
            fistatus2=loanlead.fistatus2

            allperson1 = Personmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(admin='Y') & ~Q(personcode=fleadpersoncode)).distinct('personname')
            allperson2 = Personmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(admin='Y') & ~Q(personcode=fsecondpersoncode)).distinct('personname')
            loanmast = Loanmaster.objects.filter(locationcode=loginlocationcode,apploandate__gte=fleaddate,status='A')

            fdate = loginrundate.strftime("%Y-%m-%d")

            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'fappname':fappname,
                    'fappmaritalstatus':fappmaritalstatus,
                    'fappgender':fappgender,
                    'fappmobileno':fappmobileno,
                    'fappshoplocation':fappshoplocation,
                    'fappbusiness':fappbusiness,
                    'fleaddate':fleaddate,
                    'fleadpersonname':fleadpersonname,
                    'fsecondpersonname':fsecondpersonname,
                    'floanleadid':floanleadid,
                    'ffidate1':ffidate1,
                    'ffidate2':ffidate2,
                    'fistatus1':fistatus1,
                    'fistatus2':fistatus2,
                    'allperson1':allperson1,
                    'allperson2':allperson2,
                    'loanmast':loanmast,
                    'fdate':fdate,
                        }

            if updatefi1 and fistatus1 =='N':
                return render(request,"admssapp/loanlead1update.html", context)                

            elif updatefi2 and fistatus2 =='N':
                return render(request,"admssapp/loanlead2update.html", context)                

            elif disburse and fistatus1 =='Y' and fistatus2 =='Y':
                return render(request,"admssapp/loanlead3update.html", context)    

            elif changeperson:
                return render(request,"admssapp/loanlead4update.html", context)    

            elif deleteentry:
                return render(request,"admssapp/loanleaddelete.html", context)    

            else:
            
                message = "FI Status Incomplete ..."
                messages.success(request, message)
                return render(request,"admssapp/loanleadupdate.html", context)     





##################################
######## UPDATE FI-1 COMMIT ######
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanlead1updatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                floanleadid = 0
                if len(request.POST.get('floanleadid')) >0 :
                    floanleadid = int(request.POST.get('floanleadid'))


                ffistatus =  (request.POST.get('fistatus'))
                fremark =  (request.POST.get('remark'))
                ftodaydate =  (request.POST.get('todaydate'))

                loanlead = Loanlead.objects.get(id=floanleadid)
                fappname = loanlead.appname
                fappmobileno = loanlead.appmobileno
                fappbusiness = loanlead.appbusiness


        
                loanlead.fidate1 = ftodaydate
                loanlead.fistatus1 = 'Y'
                loanlead.firemark1 = ffistatus + fremark
                if loanlead.fistatus2 == 'Y':
                    loanlead.status = 'C'


                loanlead.save()


                message = ""

                messages.success(request, message)
                return HttpResponseRedirect('/loanleadnew/')



##################################
######## UPDATE FI-2 COMMIT ######
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanlead2updatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                floanleadid = 0
                if len(request.POST.get('loanleadid')) >0 :
                    floanleadid = int(request.POST.get('loanleadid'))


                fremark =  (request.POST.get('remark'))
                ftodaydate =  (request.POST.get('todaydate'))

                loanlead = Loanlead.objects.get(id=floanleadid)
                fappname = loanlead.appname
                fappmobileno = loanlead.appmobileno
                fappbusiness = loanlead.appbusiness

        
                loanlead.fidate2 = ftodaydate
                loanlead.fistatus2 = 'Y'
                loanlead.firemark2 = fremark
                if loanlead.fistatus1 == 'Y':
                    loanlead.status = 'C'

                loanlead.save()

                message = ""

                messages.success(request, message)
                return HttpResponseRedirect('/loanleadnew/')



#############################################
########    UPDATE LOAN DISB COMMIT    ######
#############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanlead3updatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                floanleadid = 0
                fdisbreject = ''
                if len(request.POST.get('loanleadid')) >0 :
                    floanleadid = int(request.POST.get('loanleadid'))

                if len(request.POST.get('disbreject')) >0 :
                    fdisbreject = request.POST.get('disbreject')


                loanlead = Loanlead.objects.get(id=floanleadid)
                fappname = loanlead.appname
                fappmobileno = loanlead.appmobileno
                fappbusiness = loanlead.appbusiness


                floanid =  (request.POST.get('loanid'))
                if fdisbreject == 'LOANDISBURSED':
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=floanid)   
                    message = "Loan Lead " + fappname +' / '+fappmobileno+' / '+fappbusiness+ "/ FI-3 Loan Disbursed Updated successfully..."             
                else:
                    message = "Loan Lead " + fappname +' / '+fappmobileno+' / '+fappbusiness+ "/ FI-3 Loan Rejected Updated successfully..." 

                if loanlead.fistatus1 == 'Y' and loanlead.fistatus2 == 'Y' and fdisbreject=='LOANDISBURSED':
                    loanlead.status = 'C'
                    loanlead.loandisb = 'Y'
                    loanlead.loanmaster_id = loanmast.id
                    loanlead.save()

                elif loanlead.fistatus1 == 'Y' and loanlead.fistatus2 == 'Y' and fdisbreject=='LOANREJECTED':
                    loanlead.status = 'C'
                    loanlead.loandisb = 'C'
                    loanlead.save()

                message = ""
                messages.success(request, message)
                return HttpResponseRedirect('/loanleadnew/')




#############################################
########  UPDATE CHANGE PERSON COMMIT  ######
#############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanlead4updatecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                floanleadid = 0
                fdisbreject = ''
                if len(request.POST.get('loanleadid')) >0 :
                    floanleadid = int(request.POST.get('loanleadid'))


                fleadperson = request.POST.get('leadperson')
                fsecondperson = request.POST.get('secondperson')


                loanlead = Loanlead.objects.get(id=floanleadid)
                fappname = loanlead.appname
                fappmobileno = loanlead.appmobileno
                fappbusiness = loanlead.appbusiness

                if fleadperson:
                    leadperson = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fleadperson)
                    fleadpersoncode = leadperson.personcode
                    fleadpersonname = leadperson.personname

                    loanlead.leadpersoncode = fleadpersoncode
                    loanlead.leadpersonname = fleadpersonname
    
                if fsecondperson:
                    secondperson = Personmaster.objects.get(locationcode=loginlocationcode,personcode=fsecondperson)

                    fsecondpersoncode = secondperson.personcode
                    fsecondpersonname = secondperson.personname

                    loanlead.secondpersoncode = fsecondpersoncode
                    loanlead.secondpersonname = fsecondpersonname

                loanlead.save()

                message = ""
                messages.success(request, message)
                return HttpResponseRedirect('/loanleadnew/')


###################################
######## DELETE LOAN COMMIT  ######
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleaddeletecommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
          return HttpResponseRedirect('/login')
    else:

        
            if request.method == "POST":
                floanleadid = 0
                fdisbreject = ''
                if len(request.POST.get('loanleadid')) >0 :
                    floanleadid = int(request.POST.get('loanleadid'))

                loanlead = Loanlead.objects.get(id=floanleadid).delete()


                message = ""        

                messages.success(request, message)
                return HttpResponseRedirect('/loanleadnew/')



################################
####### LOAN LEADS REPORT ######
################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleadreport(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['B','A']):
                return HttpResponseRedirect('/login')
         else:
   

                allperson = Personmaster.objects.filter(locationcode=loginlocationcode,admin='Y').distinct('personname')
                
                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'loginstatus':loginstatus,
                        'currdate': currdate,
                        'allperson':allperson,
                          }

                if request.method == "POST":

                        fleadperson = request.POST.get('leadperson')
                        fleadname = request.POST.get('leadname')
                        fleadmobileno = request.POST.get('leadmobileno')

                        if fleadperson:

                            Loanleadsumm.objects.filter(locationcode=loginlocationcode).delete()
                            allperson = Personmaster.objects.filter(locationcode=loginlocationcode,admin='Y').distinct('personname')
                            allfi = Loanlead.objects.filter(locationcode=loginlocationcode,loandisb='N').order_by('id')
                            summallfi = Loanlead.objects.filter(locationcode=loginlocationcode,status='A').values('leadpersonname').annotate(totfi=Coalesce(Count('leadpersonname'),0))    
             
                            nooffi = 0
                            for all in allperson:
                                ffipersoncode = all.personcode
                                ffipersonname = all.personname

                                summfi1 = Loanlead.objects.filter(locationcode=loginlocationcode,leadpersoncode=ffipersoncode).aggregate(totfi=Coalesce(Count('leadpersoncode'),0))
                                summfi2 = Loanlead.objects.filter(locationcode=loginlocationcode, secondpersoncode=ffipersoncode).aggregate(totfi=Coalesce(Count('secondpersoncode'), 0))
                                summdisb1 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(leadpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus1', filter= Q(status='A') & Q(fistatus1='N')), 0))
                                summdisb2 = Loanlead.objects.filter(Q(locationcode=loginlocationcode) and (Q(secondpersoncode=ffipersoncode))).aggregate(disb=Coalesce(Count('loandisb', filter=Q(loandisb='Y') & Q(status='C')), 0), rejected=Coalesce(Count('loandisb', filter=Q(loandisb='C') & Q(status='C')), 0), active=Coalesce(Count('fistatus2', filter= Q(status='A') & Q(fistatus1='N')), 0))


                                loanleaddb = Loanleadsumm(locationcode=loginlocationcode,
                                            locationname=loginlocationname,
                                            personcode=ffipersoncode,
                                            personname=ffipersonname,
                                            leads = summfi1.get("totfi") + summfi2.get("totfi"),
                                            disb = summdisb1.get("disb"),
                                            rejected=summdisb1.get("rejected"),
                                            active=summdisb1.get("active") + summdisb2.get("active"))
                   
                                loanleaddb.save()            

                                leadsumm = Loanleadsumm.objects.filter(locationcode=loginlocationcode, personcode=fleadperson).order_by('personname')

                                alllead = Loanlead.objects.filter(Q(locationcode=loginlocationcode) & (Q(leadpersoncode=fleadperson) | Q(secondpersoncode=fleadperson)))
                                for all in alllead:
                                    all.tmppersoncode = fleadperson
                                    all.save()
                        
                                person = Personmaster.objects.filter(locationcode=loginlocationcode,personcode=fleadperson)
                                alllead = Loanlead.objects.filter(Q(locationcode=loginlocationcode) & (Q(leadpersoncode=fleadperson) | Q(secondpersoncode=fleadperson)))

                                context={'loginlocationcode':loginlocationcode,
                                         'loginlocationname':loginlocationname,
                                         'loginrundate':loginrundate,
                                         'loginstatus':loginstatus,
                                         'currdate': currdate,
                                         'alllead':alllead,
                                         'person':person,
                                         'leadsumm':leadsumm,
                                         'fleadperson':fleadperson,
                                         }
                                return render(request, 'admssapp/loanleadreportshow.html', context)

                        elif fleadname:
 
                        
                            alllead = Loanlead.objects.filter(Q(locationcode=loginlocationcode) & Q(appname__contains=fleadname))

                            context={'loginlocationcode':loginlocationcode,
                                     'loginlocationname':loginlocationname,
                                     'loginrundate':loginrundate,
                                     'loginstatus':loginstatus,
                                     'currdate': currdate,
                                     'alllead':alllead,
                                     'fleadname':fleadname,
                                      }
                            return render(request, 'admssapp/loanleadreportshow1.html', context)

                        elif fleadmobileno:
 
                            alllead = Loanlead.objects.filter(Q(locationcode=loginlocationcode) & Q(
                                appmobileno__contains=fleadmobileno))

                            context={'loginlocationcode':loginlocationcode,
                                     'loginlocationname':loginlocationname,
                                     'loginrundate':loginrundate,
                                     'loginstatus':loginstatus,
                                     'currdate': currdate,
                                     'alllead':alllead,
                                     'fleadmobileno':fleadmobileno,
                                      }
                            return render(request, 'admssapp/loanleadreportshow2.html', context)


                else:
                    return render(request, 'admssapp/loanleadreport.html', context)


################################
######## LOAN LEAD DETAIL ######
################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def loanleaddetail(request,loanlead_id):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['B','A']):
        return HttpResponseRedirect('/login')
    else:


            loanlead = Loanlead.objects.get(id=loanlead_id)
            fappname=loanlead.appname
            fappmaritalstatus=loanlead.appmaritalstatus
            fappgender=loanlead.appgender
            fappmobileno=loanlead.appmobileno
            fappshoplocation=loanlead.appshoplocation
            fappbusiness=loanlead.appbusiness
            fleaddate=loanlead.leaddate
            fleadpersoncode=loanlead.leadpersoncode
            fleadpersonname=loanlead.leadpersonname
            fsecondpersoncode=loanlead.secondpersoncode
            fsecondpersonname=loanlead.secondpersonname
            fstatus=loanlead.status
            ffidate1=loanlead.fidate1
            ffidate2=loanlead.fidate2
            ffiremark1=loanlead.firemark1
            ffiremark2=loanlead.firemark2

            fleadperson = loanlead.tmppersoncode

            context={'loginlocationcode':loginlocationcode,
                    'loginlocationname':loginlocationname,
                    'loginrundate':loginrundate,
                    'loginstatus':loginstatus,
                    'currdate':currdate,
                    'fappname':fappname,
                    'fappmaritalstatus':fappmaritalstatus,
                    'fappgender':fappgender,
                    'fappmobileno':fappmobileno,
                    'fappshoplocation':fappshoplocation,
                    'fappbusiness':fappbusiness,
                    'fleaddate':fleaddate,
                    'fleadpersonname':fleadpersonname,
                    'fsecondpersonname':fsecondpersonname,
                    'loanlead_id':loanlead_id,
                    'ffidate1':ffidate1,
                    'ffidate2':ffidate2,
                    'ffiremark1':ffiremark1,
                    'ffiremark2':ffiremark2,
                    'fleadperson':fleadperson,
                        }


            if loanlead==None:
                pass
            else:
                return render(request,"admssapp/loanleadfulldetail.html", context)






######################
####### LOGOUT  ######
######################
@login_required(login_url='login')
@csrf_exempt
@never_cache

def logout(request):
    if request.user.is_authenticated:
        del request.session['loguserid']
        django_logout(request)
        return redirect('home')
    else:
        return redirect('home')
