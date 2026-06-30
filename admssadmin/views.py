import csv
from django.shortcuts import render,redirect,HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.contrib import auth

from django.db.models import Q

from django.contrib.auth.models import User
from admssapp.models import Locationlogin
from admssapp.models import Loanmaster,Loanscheme,Personmaster
from admssapp.models import Locationlogin,Daybook,Loantrans,Transcd
from admssapp.models import Opclcashbank
from admssapp.models import Emicolldata
from admssapp.models import Rate
from admssapp.models import Gstdata
from admssapp.models import Crifdata
from admssapp.models import Licdata
from admssapp.models import Auditloanmaster20202021, Auditloanrecov20192020, Auditloanmaster20212022, Auditloanmaster20222023, Auditloanmaster20232024, Auditloanmaster20242025,Auditloanmaster20252026 
from admssapp.models import Daydrcr
from admssapp.models import Authcenterexpance

from django.contrib import messages

from admssapp.models import Userlogged
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
from django.db.models import Sum,Count
from django.db.models.functions import Coalesce

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout as django_logout

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout as django_logout

from admssapp.utils import render_to_pdf
from num2words import num2words

from admssapp.updateledger import update
from admssapp.updateemi import statices



########## ADMIN HOME  ###########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminhome(request):
        
        loguserid = request.session['loguserid']

        ll=Locationlogin.objects.get(user_id=loguserid)
      
        loginlocationcode=ll.locationcode
        loginlocationname=ll.locationname
        loginrundate=ll.rundate
        loginstatus = ll.status

        ip = request.session.get('ip', 0)
        x_forw = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forw:
            ip = x_forw.split(',')[-1].strip
        else:
            ip = request.META.get('REMOTE_ADDR')



        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in (['H']):
            return HttpResponseRedirect('/login')
        else:



                       ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                       ftodate = ffromdate + timedelta(days=5)
          
                       nac = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year = loginrundate.year,status="A").aggregate(total = Count("loanid"))
                       namt = Loanmaster.objects.filter(apploandate__month = loginrundate.month,apploandate__year = loginrundate.year,status="A").aggregate(total = Sum("apploanamt"))
               
                       last_14_days = loginrundate - timedelta(days=14)

                       irac = Loanmaster.objects.filter(applastemidepdate__lte=last_14_days,status="A").aggregate(total = Count("loanid"))
                       iramt = Loanmaster.objects.filter(applastemidepdate__lte=last_14_days,status="A").aggregate(total = Sum("apploanemi"))

                       sac = Loanmaster.objects.filter(apploansettlementdate__month = loginrundate.month,apploansettlementdate__year = loginrundate.year,status="C").aggregate(total = Count("loanid"))
                       samt = Loanmaster.objects.filter(apploansettlementdate__month = loginrundate.month,apploansettlementdate__year = loginrundate.year,status="C").aggregate(total = Sum("apploanamt"))

                       tac = Loanmaster.objects.filter(status="A").aggregate(total=Coalesce(Count('loanid'),0))
                       tamt = Loanmaster.objects.filter(status="A").aggregate(total=Coalesce(Sum('apploanamt'),0))
                       temi = Loanmaster.objects.filter(status="A").aggregate(total=Coalesce(Sum('apploanemi'),0))
                 
                       eac = Daybook.objects.filter(date__range=(ffromdate,ftodate),transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Count('loanid',distinct=True),0))
                       eamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),transcd__in=['3011','3012','3019','3013']).aggregate(total=Coalesce(Sum('amount'),0))

                
                       newac = nac.get("total")
                       newamt = namt.get("total")

   
                       settleac = sac.get("total")
                       settleamt = samt.get("total")

                       totalac = tac.get("total")
                       totalamt = tamt.get("total")
                       totalemi = temi.get("total")

                       emiac = eac.get("total")
                       emiamt = eamt.get("total")

                       iregac = irac.get("total")
                       iregamt = iramt.get("total")

                       if totalac!=0:
                           emicoll = round(emiac*100/totalac)
                       else:
                           emicoll= 0
                           

                       fmonth = ll.rundate.strftime("%b")
                       fyear = ll.rundate.year

                               
                       start_week = loginrundate - timedelta(loginrundate.weekday())
                       end_week = start_week + timedelta(5)

                       start_week = start_week.strftime("%d'%b%y")
                       end_week = end_week.strftime("%d'%b%y")


                       context={'loginlocationcode' : loginlocationcode,
                               'loginlocationname' : loginlocationname,
                               'loginrundate' : loginrundate,
                               'loginstatus' : loginstatus,
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
                               'ip':ip,
                                }
 
                       return render(request, 'admssadmin/home.html', context )



@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmineod(request):

                    loguserid = request.session['loguserid']
                    ll=Locationlogin.objects.get(user=loguserid)
        
                    loginlocationcode=ll.locationcode
                    loginlocationname=ll.locationname
                    loginrundate=ll.rundate
                    loginstatus = ll.status

                    user = User.objects.get(id=loguserid)
                    if user is not None and loginstatus not in (['H']):
                        return HttpResponseRedirect('/login')
                    else:
               
                            mll = Locationlogin.objects.all()


                            myrundate = mll[0].rundate
                            flogindate = myrundate + timedelta(1)
                       
                            if flogindate.isoweekday() == 7:
                                flogindate = myrundate + timedelta(2)

                                               
                            context = {
                                'loginlocationcode': loginlocationcode,
                                'loginlocationname': loginlocationname,
                                'loginrundate': loginrundate,
                                'frundate': loginrundate,
                                'flogindate': flogindate,
                                 }                     


                            if request.method == "POST":
                                frundate = request.POST.get('rundate')
                                flogindate = request.POST.get('logindate')

                                fdrundate = datetime.strptime(frundate, "%Y-%m-%d").date()
                                fdlogindate = datetime.strptime(flogindate, "%Y-%m-%d").date()


                                mll = Locationlogin.objects.all()

                                if fdlogindate <= date.today():
                                   if fdlogindate.isoweekday() == 7:
                                        message = "Sunday login Dennied , Unable to perform End of Day."
                                        messages.success(request, message)
                                        return HttpResponseRedirect('/admssadmineod/')
                                else:
                                    message = "Unable to Perform End of Day.Advance login not allowed."
                                    messages.success(request, message)
                                    return HttpResponseRedirect('/admssadmineod/')



                                for myll in mll:
                                    myll.rundate = fdlogindate
                                    myll.save()

                                mallopcl = Opclcashbank.objects.filter(date=frundate)

                                for a in mallopcl:
                                        mlocationcode = a.locationcode
                                        mlocationname = a.locationname
                                        mdate = fdlogindate
                                        mbankac = a.bankac
                                        mbankacname = a.bankacname
                                        mbankacname = a.bankacname
                                        mbankname = a.bankname
                                        mbankcode = a.bankcode
                                        mbankbranch = a.bankbranch
                                        mbankifsc = a.bankifsc
                                        muser_id = a.user_id
                                        mbankpmt = a.bankpmt
                                        mbankrec = a.bankrec
                                        mcashpmt = a.cashpmt
                                        mcashrec = a.cashrec
                                        mclcash = a.clcash
                                        mclbank = a.clbank
                                        macamt = a.acamt
                                        mhqamt = a.hqamt
                                        muserid = a.user_id
                                        mdefaultbank = a.defaultbank

                                        mnewrec = Opclcashbank(locationcode=mlocationcode,
                                            locationname=mlocationname,date=mdate,
                                            bankac=mbankac,
                                            bankacname=mbankacname,
                                            bankname=mbankname,
                                            bankcode=mbankcode,
                                            bankbranch=mbankbranch,
                                            bankifsc=mbankifsc,
                                            user_id=muserid,
                                            opcash=mclcash,
                                            clcash=mclcash,
                                            opbank=mclbank,
                                            clbank=mclbank,
                                            acamt=macamt,
                                            hqamt=mhqamt,
                                            defaultbank=mdefaultbank
                                            )
                                        mnewrec.save()
                        

                                allloan = Loanmaster.objects.filter(status='A')
                                for x in allloan:
                                        fapploanid = x.loanid
                                        loginlocationcode = x.locationcode
                                        fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                                        yloanid = Loanmaster.objects.get(loanid=fapploanid)
                                        yloanid.instdue = fcurremidue
                                        yloanid.instdone = fcurremidone
                                        finstoverdue = fcurremidue - fcurremidone

                                        if finstoverdue < 0:
                                            finstoverdue = 0
                        
                                        yloanid.instoverdueamt = yloanid.apploanemi*finstoverdue
                                        yloanid.instoverdue = finstoverdue

                                        yloanid.save()


                                message = "End of Day "+frundate+" Performed Successfully. Welcome in "+flogindate
                                messages.success(request, message)
                                return HttpResponseRedirect('/admssadmineod/')

                            return render(request, 'admssadmin/admssadmineod.html', context)


########################################
####  HQ DASHBOARD NEW LOAN REPORT  ####
########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardadmssadminnewloanreport(request):

     loguserid = request.session['loguserid']
     ll = Locationlogin.objects.get(user=loguserid)

     loginlocationcode = ll.locationcode
     loginlocationname = ll.locationname
     loginrundate = ll.rundate
     loginstatus = ll.status
     currdate = date.today()

     user = User.objects.get(id=loguserid)
     if user is not None and loginstatus not in (['H']):
          return HttpResponseRedirect('/login')
     else:

            ffromdate = ll.rundate
            ftodate = ll.rundate

            allr = Loanmaster.objects.filter(apploandate__month=loginrundate.month, apploandate__year=loginrundate.year).order_by('locationcode','apploandate', 'id')
            newac = Loanmaster.objects.filter(apploandate__month=loginrundate.month, apploandate__year=loginrundate.year, status="A").values('locationcode', 'locationname').annotate(totac=Count("loanid"), totloan=Sum("apploanamt"), totemi=Sum("apploanemi"))

            ffromdate = loginrundate.strftime("%Y-%m-01")
            ftodate = loginrundate.strftime("%Y-%m-%d")

            context = {'loginlocationcode': loginlocationcode,
                       'loginlocationname': loginlocationname,
                       'loginrundate': loginrundate,
                       'ffromdate': ffromdate,
                       'ftodate': ftodate,
                       'currdate': currdate,
                       'allr': allr,
                       'newac': newac,
                         }

            return render(request, 'admssadmin/admssadminnewloanreportshow.html', context)



###########################################
####  HQ DASHBOARD EMI DEPOSIT REPORT  ####
###########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardadmssadminemidepositreport(request):

    loguserid = request.session['loguserid']
    ll = Locationlogin.objects.get(user=loguserid)

    loginlocationcode = ll.locationcode
    loginlocationname = ll.locationname
    loginrundate = ll.rundate
    loginstatus = ll.status
    currdate = date.today()

    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in (['H']):
         return HttpResponseRedirect('/login')
    else:

         ffromdate = ll.rundate
         ftodate = ll.rundate


         ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
         ftodate = ffromdate + timedelta(days=5)

         allr = Loantrans.objects.filter(date__range=(ffromdate, ftodate)).select_related('master')

         for all in allr:
            if all.amount >= all.master.apploanemi:
               all.flag="Y"
            else:
               all.flag="N"
               all.save()

         allr = Loantrans.objects.filter(date__range=(ffromdate,ftodate)).order_by('locationcode','date','id')

         emidep = Loantrans.objects.filter(date__range=(ffromdate, ftodate)).values('locationcode', 'locationname').annotate(totac=Count("loanid",distinct=True), totamt=Sum("amount"))

         #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
         #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

         context = {'loginlocationcode': loginlocationcode,
                     'loginlocationname': loginlocationname,
                     'loginrundate': loginrundate,
                       'ffromdate': ffromdate,
                       'ftodate': ftodate,
                       'currdate': currdate,
                       'allr': allr,
                       'emidep': emidep,
                     }

         return render(request, 'admssadmin/admssadminemidepositreportshow.html', context)


##################################
#### DASHBOARD EMI DUE REPORT ####
##################################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def dashboardadmssadminemiduereport(request):

     loguserid = request.session['loguserid']
     ll = Locationlogin.objects.get(user=loguserid)

     loginlocationcode = ll.locationcode
     loginlocationname = ll.locationname
     loginrundate = ll.rundate
     loginstatus = ll.status
     currdate = date.today()

     user = User.objects.get(id=loguserid)

     if user is not None and loginstatus not in (['H']):
         return HttpResponseRedirect('/login')
     else:

                 fdate = ll.rundate

                 last_14_days = loginrundate - timedelta(days=14)
                 ffromdate = last_14_days
                 ftodate = ll.rundate


                 summallr = Loanmaster.objects.filter(applastemidepdate__lte=last_14_days, appemiduedate__lt=last_14_days, status="A").values(
                     'locationcode', 'locationname').annotate(totac=Count("loanid"), totemi=Sum("apploanemi"), totbalamt=Sum("apploanbalamt"),)


                 allr = Loanmaster.objects.filter(locationcode=loginlocationcode, applastemidepdate__lte=last_14_days,
                                                  appemiduedate__lt=last_14_days, status="A").order_by('applastemidepdate')
                 context = {'loginlocationcode': loginlocationcode,
                             'loginlocationname': loginlocationname,
                             'loginrundate': loginrundate,
                             'currdate': currdate,
                             'fdate': fdate,
                             'allr': allr,
                             'summallr': summallr,
                             }

                 return render(request, 'admssadmin/admssadminemiirregulareportshow.html', context)





#############################
####  HQ NEW LOAN REPORT ####
#############################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminnewloanreport(request):

     loguserid = request.session['loguserid']
     ll = Locationlogin.objects.get(user=loguserid)
     loginlocationcode = ll.locationcode
     loginlocationname = ll.locationname
     loginrundate = ll.rundate
     loginstatus = ll.status
     currdate = date.today()

     user = User.objects.get(id=loguserid)
     if user is not None and loginstatus not in (['H']):
        return HttpResponseRedirect('/login')
     else:

         ffromdate = ll.rundate
         ftodate = ll.rundate

         context = {'loginlocationcode': loginlocationcode,
                    'loginlocationname': loginlocationname,
                    'loginrundate': loginrundate,
                    'currdate': currdate,
                    'ffromdate': ffromdate,
                    'ftodate': ftodate,
                          }

         if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')

                    newac = Loanmaster.objects.filter(apploandate__range=(
                        ffromdate, ftodate), status="A").values('locationcode', 'locationname').annotate(totac=Count("loanid"), totloan=Sum("apploanamt"), totemi=Sum("apploanemi"))

                    allr = Loanmaster.objects.filter(apploandate__range=(
                        ffromdate, ftodate), status="A").order_by('locationcode', 'apploandate', 'id')


                    #ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    #ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    context = {'loginlocationcode': loginlocationcode,
                                'loginlocationname': loginlocationname,
                                    'loginrundate': loginrundate,
                                    'ffromdate': ffromdate,
                                    'ftodate': ftodate,
                                    'currdate': currdate,
                                    'allr': allr,
                                    'newac':newac,
                                       }

                    return render(request, 'admssadmin/admssadminnewloanreportshow.html', context)

         else:
             return render(request, 'admssadmin/admssadminnewloanreport.html', context)



################################################
###### HQ EMI COLLECTOR COLLECTION REPORT ######
################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmincollemireportbranch(request):
     
         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user_id=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus = ll.status
         currdate = date.today()
         user = User.objects.get(id=loguserid)


         if user is not None and loginstatus not in(['H']):
                return HttpResponseRedirect('/login')
         else:

                ffromdate = ll.rundate
                ftodate = ll.rundate

                context={'loginlocationcode':loginlocationcode,
                         'loginlocationname':loginlocationname,
                         'loginrundate':loginrundate,
                         'currdate': currdate,
                         'ffromdate': ffromdate,
                         'ftodate': ftodate,
                          }
        

                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')

                    allr = Loantrans.objects.filter(date__range=(
                        ffromdate, ftodate)).select_related('master')

                    for all in allr:
                        if all.amount >= all.master.apploanemi:
                            all.flag="Y"
                        else:
                            all.flag="N"
                        all.save()

                    allr = Loantrans.objects.filter(date__range=(ffromdate,ftodate)).order_by('locationcode','date','id')

                    emidep = Loantrans.objects.filter(date__range=(
                            ffromdate, ftodate)).values('locationcode', 'locationname').annotate(totac=Count("loanid",distinct=True), totamt=Sum("amount"))

                    ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    ftodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    context={'loginlocationcode':loginlocationcode,
                             'loginlocationname':loginlocationname,
                             'loginrundate':loginrundate,
                             'currdate': currdate,
                             'ffromdate': ffromdate,
                             'ftodate': ftodate,
                             'allr' : allr,
                             'emidep': emidep,
                            }
                    return render(request, 'admssadmin/admssadminemidepositreportshow.html', context)

                return render(request, 'admssadmin/admssadminemidepositreport.html', context)
            

###########################
#### HQ EMI DUE REPORT ####
###########################

@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminemiduereport(request):

    loguserid = request.session['loguserid']
    ll = Locationlogin.objects.get(user=loguserid)

    loginlocationcode = ll.locationcode
    loginlocationname = ll.locationname
    loginrundate = ll.rundate
    fduedate = loginrundate
    loginstatus = ll.status

    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in (['H']):
         return HttpResponseRedirect('/login')
    else:

              context = {'loginlocationcode': loginlocationcode,
                          'loginlocationname': loginlocationname,
                           'loginrundate': loginrundate,
                           'fduedate': fduedate,
                          }

              if request.method == "POST":

                    fduedate = request.POST.get('duedate')
                    fwise = request.POST.get('nameid')


                    fduedate = datetime.strptime(fduedate, "%Y-%m-%d").date()

                    allr = Loanmaster.objects.filter(status="A")
                    for all in allr:

                        if all.applastemidepdate is not None:
                            all.delaydays3 = (
                                fduedate-all.applastemidepdate).days

                        if all.appemiduedate.strftime('%w') == fduedate.strftime('%w'):
                            all.delaydays1 = 1
                            all.delaydays2 = 0

                        else:
                            all.delaydays1 = 0
                            all.delaydays2 = 0

                        if all.applastemidepdate is not None:
                            if (fduedate-all.applastemidepdate).days >= 7 and (fduedate-all.applastemidepdate).days <= 14:
                                all.delaydays1 = 1
                                all.delaydays2 = 1
                            elif (fduedate-all.applastemidepdate).days > 14:
                                all.delaydays1 = 1
                                all.delaydays2 = 2

                            elif (fduedate-all.applastemidepdate).days <= 4:
                                all.delaydays1 = 0
                                all.delaydays2 = 0

                        if all.appemiduedate.strftime('%w') == fduedate.strftime('%w'):
                            all.delaydays1 = 1

                            if all.applastemidepdate is not None:
                                if (fduedate-all.applastemidepdate).days >= 0 and (fduedate-all.applastemidepdate).days <= 14:
                                    all.delaydays2 = 1

                                elif (fduedate-all.applastemidepdate).days > 14:
                                    all.delaydays2 = 2

                        all.save()

    
                        allr = Loanmaster.objects.filter(delaydays1__in=[1], status="A").values('locationcode', 'locationname').annotate(totac=Count('loanid')).annotate(totemi=Coalesce(Sum('apploanemi'), 0)).order_by('locationcode')

                
                    
                        context = {'loginlocationcode': loginlocationcode,
                                   'loginlocationname': loginlocationname,
                                   'loginrundate': loginrundate,
                                   'fduedate': fduedate,
                                   'allr': allr,
                                    }

                    return render(request, 'admssadmin/admssadminemiduereportshow.html', context)

              else:
                    return render(request, 'admssadmin/admssadminemiduereport.html', context)




##### PROCESING FEES RECEIPTS PRINTING #####
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminprocessingfeereceipt(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:


                allbranch = Locationlogin.objects.filter(status__in=['B', 'A']).order_by('id')
                context = {'loginlocationcode': loginlocationcode,
                           'loginlocationname': loginlocationname,
                           'loginrundate': loginrundate,
                           'allbranch': allbranch,
                           }

                return render(request, 'admssadmin/admssadminprocessingfeereceipt.html', context)



#### PROCESING FEES RECEIPTS PRINTING GET ###
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminprocessingfeereceiptget(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:


                if request.method == "POST":
                    freceipttype = request.POST.get('receipttype')
                    fbranchname = request.POST.get('branchname')


                allbranch = Locationlogin.objects.get(locationcode=fbranchname,status__in=['B', 'A'])
                restall = Loanmaster.objects.filter(locationcode=fbranchname, procfeereceipt = 'N').order_by('apploandate','id')
                flocationcode = allbranch.locationcode
                flocationname = allbranch.locationname
                context = {
                               'flocationcode': flocationcode,
                               'flocationname': flocationname,
                               'freceipttype':freceipttype,
                               'fbranchname':fbranchname,
                               'restall': restall,
                                }

                return render(request, 'admssadmin/admssadminprocessingfeereceiptget.html', context)





#### PROCESING FEES RECEIPTS PRINTING PRINT ####
################################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminprocessingfeereceiptprint(request):

           loguserid = request.session['loguserid']
           ll = Locationlogin.objects.get(user=loguserid)

           loginlocationcode = ll.locationcode
           loginlocationname = ll.locationname
           loginrundate = ll.rundate
           loginstatus = ll.status

           user = User.objects.get(id=loguserid)
           if user is not None and loginstatus not in (['H']):
                return HttpResponseRedirect('/login')
           else:

                if request.method == "POST":
                    freceipttype = request.POST.get('receipttype')
                    fbranchname = request.POST.get('branchname')
                    floanid = request.POST.get('loanid')


                    printid = Loanmaster.objects.get(loanid=floanid)

                    flocationcode = printid.locationcode
                    flocationname = printid.locationname



                    processingfee = (printid.apploanamt)*.01
                    pfee = ('%.2f' % processingfee)
                    cgst = processingfee*.09
                    sgst = processingfee*.09
                    gst = processingfee*.18
                    totalamt = processingfee + gst

                    inwords = num2words(totalamt)

                    pfee = ('%.2f' % processingfee)
                    cgst = ('%.2f' % cgst)
                    sgst = ('%.2f' % sgst)
                    totalamt = ('%.2f' % totalamt)

                    printid.procfeereceipt='Y'
                    printid.save()

                    context = {
                               'flocationcode': flocationcode,
                               'flocationname': flocationname,
                               'freceipttype': freceipttype,
                               'printid': printid,
                               'processingfee': processingfee,
                               'pfee': pfee,
                               'cgst': cgst,
                               'sgst': sgst,
                               'gst' : gst,
                               'totalamt' : totalamt,
                               'inwords' : inwords,
                               }

                    return render(request, 'admssadmin/admssadminprocessingfeereceiptprint.html', context)


################ GST DATA  ################
###########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmingstdata(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:

                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')

                    Gstdata.objects.all().delete()

                    allloanmast = Loanmaster.objects.filter(Q(apploandate__gte=ffromdate) & Q(apploandate__lte=ftodate)).order_by('locationcode','apploandate')
                    for x in allloanmast:
                     
                        flocationcode = x.locationcode
                        flocationname = x.locationname                        
                        floanid = x.loanid
                        fappname = x.appname
                        fappfathername = x.appfathername
                        fapploandate = x.apploandate
                        fapploanamt = x.apploanamt



                        gst = Gstdata(locationcode = flocationcode,
                                      locationname = flocationname,
                                      loanid = floanid,
                                      appname = fappname,
                                      appfathername=fappfathername,
                                      apploandate=fapploandate,
                                      apploanamt=fapploanamt,
                                      processingfee = fapploanamt/100,
                                      gstamount = ((fapploanamt/100)*.18),
                                      fromdate = ffromdate,
                                      todate = ftodate)
                        gst.save()


                    xfromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    ffromdate = xfromdate
                    ftodate = xtodate

                    fmonth = xtodate.strftime("%B")
                    fyear = str(xtodate.year)

                    gstdata = Gstdata.objects.all().only('loanid','appname','appfathername','apploandate','apploanamt','processingfee','gstamount','fromdate','todate')


                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('gstdata')
                    writer = csv.writer(response)
                    writer.writerow(['loanid','appname','appfathername','apploandate','apploanamt','processingfee','gstamount','fromdate','todate'])

                    for user in gstdata:
                        writer.writerow([user.loanid,user.appname,user.appfathername,user.apploandate,user.apploanamt,user.processingfee,user.gstamount,user.fromdate,user.todate])

                    message = "GST DATA being prepared for period..."
                    messages.success(request, message)

                    return response


               
                lastmonth = loginrundate - relativedelta(months=1)
                
                ffromdate = lastmonth.strftime("%Y-%m-01")
                ftodate = lastmonth.strftime("%Y-%m-%d")

                ffromdate = lastmonth.strftime("%Y-%m-01")
                lastdate = calendar.monthrange(lastmonth.year, lastmonth.month)[1]

                ftodate = datetime(lastmonth.year,lastmonth.month, lastdate).strftime("%Y-%m-%d")


               

                context = {'loginlocationcode': loginlocationcode,
                           'loginlocationname': loginlocationname,
                           'loginrundate': loginrundate,
                           'ffromdate': ffromdate,
                           'ftodate': ftodate,
                           }

                return render(request, 'admssadmin/admssadmingstdata.html', context)





################ CRIF DATA  ################
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmincrifdata(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:

                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')

                    #allloanmast = Loanmaster.objects.filter((Q(apploandate__lte=ftodate) & Q(status="A")) | (Q(apploansettlementdate__gte=ffromdate) & Q(apploansettlementdate__lte=ftodate))).order_by('apploandate')
                    allloanmast = Loanmaster.objects.filter((Q(status="C") | Q(status="A")) & Q(apploandate__lte=ftodate)).order_by('apploandate')

                    Crifdata.objects.all().delete()

                    for x in allloanmast:
                        lastdeposit = Loantrans.objects.filter(Q(loanid=x.loanid) & Q(
                            date__lte=ftodate)).order_by('date').last()
                        
                        if lastdeposit is not None:
                            lastdepdate = datetime.strftime(lastdeposit.date, "%d%m%Y")
                            flastemiddmmyyyy = lastdepdate
                            if len(flastemiddmmyyyy) == 7:
                                flastemiddmmyyyy = '0' + flastemiddmmyyyy
                        else:
                            flastemiddmmyyyy = ''

                        totaldep = Loantrans.objects.filter(Q(loanid=x.loanid) & Q(
                            date__lte=ftodate)).aggregate(total=Sum("amount"))

                        totaldeposit = totaldep.get("total")


                        flocationcode = x.locationcode
                        flocationname = x.locationname
                        fappname = x.appname

                        fappfirstname = ''
                        fappmiddlename = ''
                        fapplastname = ''

                        s = fappname.split(" ")
                        fappfirstname = s[0]

                        if len(s) > 1 and len(s) <= 2:
                          fapplastname = s[1]

                        if len(s) > 2 and len(s) <= 3:
                          fappmiddlename = s[1]
                          flastname = s[2]

                        fdobddmmyyyy = datetime.strftime(x.appdob, "%d%m%Y")

                        if len(fdobddmmyyyy) == 7:
                            fdobddmmyyyy = '0' + fdobddmmyyyy


                        fcoappname = x.coappname

                        fcoappfirstname = ''
                        fcoappmiddlename = ''
                        fcoapplastname = ''

                        s = fcoappname.split(" ")
                        fcoappfirstname = s[0]

                        if len(s) > 1 and len(s) <= 2:
                          fcoapplastname = s[1]

                        if len(s) > 2 and len(s) <= 3:
                          fcoappmiddlename = s[1]
                          fcolastname = s[2]


                        fcoappdobddmmyyyy = datetime.strftime(x.coappdob, "%d%m%Y")

                        if len(fcoappdobddmmyyyy) == 7:
                            fcoappdobddmmyyyy = '0' + fcoappdobddmmyyyy

                        fcoappname = x.coappname

                        fcoappfirstname = ''
                        fcoappmiddlename = ''
                        fcoapplastname = ''

                        s = fcoappname.split(" ")
                        fcoappfirstname = s[0]

                        if len(s) > 1 and len(s) <= 2:
                          fcoapplastname = s[1]

                        if len(s) > 2 and len(s) <= 3:
                          fcoappmiddlename = s[1]
                          fcoapplastname = s[2]

                        fguarname = x.guarname

                        fguarfirstname = ''
                        fguarmiddlename = ''
                        fguarlastname = ''

                        s = fguarname.split(" ")
                        fguarfirstname = s[0]

                        if len(s) > 1 and len(s) <= 2:
                          fguarlastname = s[1]

                        if len(s) > 2 and len(s) <= 3:
                          fguarmiddlename = s[1]
                          fguarlastname = s[2]


                        fguardobddmmyyyy = datetime.strftime(x.appdob, "%d%m%Y")

                        if x.appgender == 'M':
                            gender = "1"
                        else:
                            gender = "2"

                        fgender = gender
                        fpanno = x.apppanno
                        fpassportno = ''
                        fvoteridno = ''
                        fdlno = ''
                        frationcardno = '' 
                        fuid = x.appadharno
                        faid = ''
                        ftelephoneno1 = x.appmobileno
                        ftelephonetype1 = '02'
                        ftelephoneno2 = ''
                        ftelephonetype2 = ''
                        ftelephoneno3 = ''
                        ftelephonetype3 = ''
                        ftelephoneext = ''
                        femailid = ''
                        fconsumeradd1 = x.apppresentadd
                        fconsumercity1 = x.apppresentaddcity
                        fconsumerdistrict1 = x.apppresentaddcity
                        fconsumerstatecode1 = '33'
                        fconsumerpincode1 = x.apppresentaddpin
                        fconsumeraddcategory1 = '02'
                        fconsumerresicode1 = ''
                        fconsumeradd2 = ''
                        fconsumercity2 = ''
                        fconsumerdistrict2 = ''
                        fconsumerstatecode2 = ''
                        fconsumerpincode2 = ''
                        fconsumeraddcategory2 = ''
                        fconsumerresicode2 = ''
                        fmembercode = x.loanid
                        fmembershortname = x.appname
                        floanacno = x.loanid
                        facnotype = '40'
                        fownershipindi = '1'



                        #if x.guargender == 'M':
                        #    gender = "1"
                        #else:
                        #    gender = "2"

                        gender = "1"    
                        fguargender = gender
                        fguarpanno = x.guarpanno
                        fguarpassportno = ''
                        fguarvoteridno = ''
                        fguardlno = ''
                        fguarrationcardno = '' 
                        fguaruid = x.guaradharno
                        fguaraid = ''
                        fguartelephoneno1 = x.guarmobileno
                        fguartelephonetype1 = '02'
                        fguartelephoneno2 = ''
                        fguartelephonetype2 = ''
                        fguartelephoneno3 = ''
                        fguartelephonetype3 = ''
                        fguartelephoneext = ''
                        fguaremailid = ''
                        fguarconsumeradd1 = x.guarpresentadd
                        fguarconsumercity1 = x.guarpresentaddcity
                        fguarconsumerdistrict1 = x.guarpresentaddcity
                        fguarconsumerstatecode1 = '33'
                        fguarconsumerpincode1 = x.guarpresentaddpin
                        fguarconsumeraddcategory1 = '02'
                        fguarconsumerresicode1 = ''
                        fguarconsumeradd2 = ''
                        fguarconsumercity2 = ''
                        fguarconsumerdistrict2 = ''
                        fguarconsumerstatecode2 = ''
                        fguarconsumerpincode2 = ''
                        fguarconsumeraddcategory2 = ''
                        fguarconsumerresicode2 = ''
                        fguarmembercode = x.loanid
                        fguarmembershortname = x.guarname
                        floanacno = x.loanid
                        facnotype = '40'
                        fguarownershipindi = '3'

                        floandtddmmyyyy = datetime.strftime(x.apploandate, "%d%m%Y")
                        if len(floandtddmmyyyy) == 7:
                            floandtddmmyyyy = '0' + floandtddmmyyyy
                            
                        #lastemiddmmyyyy = datetime.strftime(lastdepdate, "%d%m%Y")
                        if x.apploansettlementdate is not None:
                            fclosedtddmmyyyy = datetime.strftime(x.apploansettlementdate, "%d%m%Y")
                            if len(fclosedtddmmyyyy) == 7:
                                fclosedtddmmyyyy = '0' + fclosedtddmmyyyy
                        else:
                            fclosedtddmmyyyy = ''
                        
                        freportdate = datetime.strptime(ftodate, "%Y-%m-%d").date()
                        freportdateddmmyyyy = datetime.strftime(freportdate, "%d%m%Y")
                        if len(freportdateddmmyyyy) == 7:
                            freportdateddmmyyyy = '0' + freportdateddmmyyyy

                        floanamount = x.apploanamt
                        fcurruntbalance = x.apploandueamt - x.apptotalrecamt

                        famountoverdue = ''
                        fnumberofdayspast = 0
                        foldmembercode = ''
                        foldmembershortname = ''
                        foldloanacno = ''
                        foldacnotype = ''
                        foldownershipindi = ''
                        fsuitfiled = ''
                        fwrittenoff = ''
                        fassetclassification = '' 
                        fvalueofcollateral = ''
                        ftypeofcollateral = ''
                        fcreditlimit = x.apploanamt
                        fcashlimit = ''
                        froi = ''
                        frepaymenttenure = '' 
                        femiamount = x.apploanemi
                        fwrittenofamounttotal = '' 
                        fwrittenofamountprin = ''
                        fsettlementamount = ''
                        fpaymentgrequency = ''
                        factualpaymentamount = ''
                        foccupationcode = ''
                        fincome = ''
                        fnetincomeindicator = '' 
                        fmonthlyincomeindicator = '' 

                        loginlocationcode = x.locationcode
                        fappname = x.appname
                        fapploanid = x.loanid
                        fapploanamt = x.apploanamt
                        fapploanint = x.apploanint
                        fapploanemi = x.apploanemi
                    
                        fapploandate = x.apploandate
                        fapploantenr = x.apploantenr
                        #delta = loginrundate - x.apploandate
                        xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()
                        delta = xtodate - x.apploandate
                        fapploandays = delta.days
                        fappemifreq = x.appemifreq
                        floantype = x.loantype
                        fapplastemidepdate = x.applastemidepdate
                        fappemiduedate = x.appemiduedate

                        fapptotalrecamt = x.apptotalrecamt
                        fapptotaldueamt = x.apploanamt + x.apploanint
                        fapptotalbalamt = x.apploanamt + x.apploanint - x.apptotalrecamt
                        fcurruntbalance = x.apploanamt - x.appprinrecamt

                        loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

                        #fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)


                  

                        acurrdueamt = 0
                        afcurrdueamt = 0
                        afexcessint = 0
                    
                        fappbalamt = 0
                
                        fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)



                        famountoverdue = fcurroverdue


                        if fapptotalbalamt > fcurrdueamt :
                            fcurrdueamt = fapptotalbalamt
                       
                        if fcurrdueamt < fapploanemi:
                            famountoverdue = 0

                        
                        if fcurrdueamt > fapploanamt :
                            fcurrdueamt = fapploanamt

                        if totaldays > fapploantenr :
                            famountoverdue = fcurrdueamt

                        if x.apploansettlementdate is not None:
                            fcurrdueamt=0
                            famountoverdue=0


                        if fcurrdueamt < 0 :
                            fcurrdueamt=0

                        if famountoverdue < 0:
                            famountoverdue = 0


        
                        xfromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                        xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()


                        if x.writtenoff == 'Y':
                            fwrittenoff = '02'
                            fwrittenofamounttotal = x.writtenofamounttotal
                            fwrittenofamountprin = x.writtenofamountprin
                        else:
                            fwrittenoff = ''
                            fwrittenofamountprin = ''
                            fwrittenofamountprin = ''

                        if fapploanid == 'I100100000377' or fapploanid == 'I100100000650' or fapploanid == 'I100100000333':
                            print(fappname,fapploanid,x.status,totaldays,fapploantenr,fcurrdueamt,famountoverdue)

                        if fpanno != 'AQYPS8789E':

                            crif = Crifdata(locationcode = flocationcode,
                                            locationname = flocationname,
                                            appname = fappname,
                                            firstname=fappfirstname,
                                            middlename=fappmiddlename,
                                            lastname=fapplastname,
                                            dobddmmyyyy = fdobddmmyyyy,
                                            gender = fgender,
                                            panno = fpanno,
                                            passportno = fpassportno,
                                            voteridno = fvoteridno,
                                            dlno = fdlno,
                                            rationcardno = frationcardno,
                                            uid = fuid,
                                            aid = faid,
                                            telephoneno1 = ftelephoneno1,
                                            telephonetype1 = ftelephonetype1,
                                            telephoneno2 = ftelephoneno2,
                                            telephonetype2 = ftelephonetype2,
                                            telephoneno3 = ftelephoneno3,
                                            telephonetype3 = ftelephonetype3,
                                            telephoneext = ftelephoneext,
                                            emailid = femailid,
                                            consumeradd1 = fconsumeradd1,
                                            consumercity1 = fconsumercity1,
                                            consumerdistrict1 = fconsumerdistrict1,
                                            consumerstatecode1 = fconsumerstatecode1,
                                            consumerpincode1 = fconsumerpincode1,
                                            consumeraddcategory1 = fconsumeraddcategory1,
                                            consumerresicode1 = fconsumerresicode1,
                                            consumeradd2 = fconsumeradd2,
                                            consumercity2 = fconsumercity2,
                                            consumerdistrict2 = fconsumerdistrict2,
                                            consumerstatecode2 = fconsumerstatecode2,
                                            consumerpincode2 = fconsumerpincode2,
                                            consumeraddcategory2 = fconsumeraddcategory2,
                                            consumerresicode2 = fconsumerresicode2,
                                            membercode = fmembercode,
                                            membershortname = fmembershortname,
                                            loanacno = floanacno,
                                            acnotype = facnotype,
                                            ownershipindi = fownershipindi,
                                            loandtddmmyyyy = floandtddmmyyyy,
                                            lastemiddmmyyyy = flastemiddmmyyyy,
                                            closedtddmmyyyy = fclosedtddmmyyyy,
                                            reportdateddmmyyyy = freportdateddmmyyyy,
                                            loanamount = floanamount,
                                            curruntbalance = fcurrdueamt,
                                            amountoverdue = famountoverdue,
                                            numberofdayspast = fnumberofdayspast,
                                            oldmembercode = foldmembercode,
                                            oldmembershortname = foldmembershortname,
                                            oldloanacno = foldloanacno,
                                            oldacnotype = foldacnotype,
                                            oldownershipindi = foldownershipindi,
                                            suitfiled = fsuitfiled,
                                            writtenoff = fwrittenoff,
                                            assetclassification = fassetclassification,
                                            valueofcollateral = fvalueofcollateral,
                                            typeofcollateral = ftypeofcollateral,
                                            creditlimit = fcreditlimit,
                                            cashlimit = fcashlimit,
                                            roi = froi,
                                            repaymenttenure = frepaymenttenure,
                                            emiamount = femiamount,
                                            writtenofamounttotal = fwrittenofamounttotal,
                                            writtenofamountprin = fwrittenofamountprin,
                                            settlementamount = fsettlementamount,
                                            paymentgrequency = fpaymentgrequency,
                                            actualpaymentamount = factualpaymentamount,
                                            occupationcode = foccupationcode,
                                            income = fincome,
                                            netincomeindicator = fnetincomeindicator,
                                            monthlyincomeindicator = fmonthlyincomeindicator
                                            )
                            crif.save()

                            if fguarpanno != 'AQYPS8789E':

                                crif = Crifdata(locationcode = flocationcode,
                                                locationname = flocationname,
                                                appname = fguarname,
                                                firstname=fguarfirstname,
                                                middlename=fguarmiddlename,
                                                lastname=fguarlastname,
                                                dobddmmyyyy = fguardobddmmyyyy,
                                                gender = fguargender,
                                                panno = fguarpanno,
                                                passportno = fguarpassportno,
                                                voteridno = fguarvoteridno,
                                                dlno = fguardlno,
                                                rationcardno = fguarrationcardno,
                                                uid = fguaruid,
                                                aid = fguaraid,
                                                telephoneno1 = fguartelephoneno1,
                                                telephonetype1 = fguartelephonetype1,
                                                telephoneno2 = fguartelephoneno2,
                                                telephonetype2 = fguartelephonetype2,
                                                telephoneno3 = fguartelephoneno3,
                                                telephonetype3 = fguartelephonetype3,
                                                telephoneext = fguartelephoneext,
                                                emailid = fguaremailid,
                                                consumeradd1 = fguarconsumeradd1,
                                                consumercity1 = fguarconsumercity1,
                                                consumerdistrict1 = fguarconsumerdistrict1,
                                                consumerstatecode1 = fguarconsumerstatecode1,
                                                consumerpincode1 = fguarconsumerpincode1,
                                                consumeraddcategory1 = fguarconsumeraddcategory1,
                                                consumerresicode1 = fguarconsumerresicode1,
                                                consumeradd2 = fguarconsumeradd2,
                                                consumercity2 = fguarconsumercity2,
                                                consumerdistrict2 = fguarconsumerdistrict2,
                                                consumerstatecode2 = fguarconsumerstatecode2,
                                                consumerpincode2 = fguarconsumerpincode2,
                                                consumeraddcategory2 = fguarconsumeraddcategory2,
                                                consumerresicode2 = fguarconsumerresicode2,
                                                membercode = fmembercode,
                                                membershortname = fguarmembershortname,
                                                loanacno = floanacno,
                                                acnotype = facnotype,
                                                ownershipindi = fguarownershipindi,
                                                loandtddmmyyyy = floandtddmmyyyy,
                                                lastemiddmmyyyy = flastemiddmmyyyy,
                                                closedtddmmyyyy = fclosedtddmmyyyy,
                                                reportdateddmmyyyy = freportdateddmmyyyy,
                                                loanamount = floanamount,
                                                curruntbalance = fcurrdueamt,
                                                amountoverdue = famountoverdue,
                                                numberofdayspast = fnumberofdayspast,
                                                oldmembercode = foldmembercode,
                                                oldmembershortname = foldmembershortname,
                                                oldloanacno = foldloanacno,
                                                oldacnotype = foldacnotype,
                                                oldownershipindi = foldownershipindi,
                                                suitfiled = fsuitfiled,
                                                writtenoff = fwrittenoff,
                                                assetclassification = fassetclassification,
                                                valueofcollateral = fvalueofcollateral,
                                                typeofcollateral = ftypeofcollateral,
                                                creditlimit = fcreditlimit,
                                                cashlimit = fcashlimit,
                                                roi = froi,
                                                repaymenttenure = frepaymenttenure,
                                                emiamount = femiamount,
                                                writtenofamounttotal = fwrittenofamounttotal,
                                                writtenofamountprin = fwrittenofamountprin,
                                                settlementamount = fsettlementamount,
                                                paymentgrequency = fpaymentgrequency,
                                                actualpaymentamount = factualpaymentamount,
                                                occupationcode = foccupationcode,
                                                income = fincome,
                                                netincomeindicator = fnetincomeindicator,
                                                monthlyincomeindicator = fmonthlyincomeindicator
                                                )
                                crif.save()


                    xfromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                    xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()

                    ffromdate = xfromdate
                    ftodate = xtodate

                    fmonth = xtodate.strftime("%B")
                    fyear = str(xtodate.year)

                    crifdata = Crifdata.objects.all().only('firstname','middlename','lastname','dobddmmyyyy','gender','panno','passportno','voteridno','dlno','rationcardno','uid','aid','telephoneno1','telephonetype1','telephoneno2','telephonetype2','telephoneno3','telephonetype3','telephoneext','emailid','consumeradd1','consumercity1','consumerdistrict1','consumerstatecode1','consumerpincode1','consumeraddcategory1','consumerresicode1','consumeradd2','consumercity2','consumerdistrict2','consumerstatecode2','consumerpincode2','consumeraddcategory2','consumerresicode2','membercode','membershortname','loanacno','acnotype','ownershipindi','loandtddmmyyyy','lastemiddmmyyyy','closedtddmmyyyy','reportdateddmmyyyy','loanamount','curruntbalance','amountoverdue','numberofdayspast','oldmembercode','oldmembershortname','oldloanacno','oldacnotype','oldownershipindi','suitfiled','writtenoff','assetclassification','valueofcollateral','typeofcollateral','creditlimit','cashlimit','roi','repaymenttenure','emiamount','writtenofamounttotal','writtenofamountprin', 'settlementamount','paymentgrequency','actualpaymentamount','occupationcode','income','netincomeindicator','monthlyincomeindicator')
            

                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('crifdata')
                    writer = csv.writer(response)
                    writer.writerow(['firstname','middlename','lastname','dobddmmyyyy','gender','panno','passportno','voteridno','dlno','rationcardno','uid','aid','telephoneno1','telephonetype1','telephoneno2','telephonetype2','telephoneno3','telephonetype3','telephoneext','emailid','consumeradd1','consumercity1','consumerdistrict1','consumerstatecode1','consumerpincode1','consumeraddcategory1','consumerresicode1','consumeradd2','consumercity2','consumerdistrict2','consumerstatecode2','consumerpincode2','consumeraddcategory2','consumerresicode2','membercode','membershortname','loanacno','acnotype','ownershipindi','loandtddmmyyyy','lastemiddmmyyyy','closedtddmmyyyy','reportdateddmmyyyy','loanamount','curruntbalance','amountoverdue','numberofdayspast','oldmembercode','oldmembershortname','oldloanacno','oldacnotype','oldownershipindi','suitfiled','writtenoff','assetclassification','valueofcollateral','typeofcollateral','creditlimit','cashlimit','roi','repaymenttenure','emiamount','writtenofamounttotal','writtenofamountprin', 'settlementamount','paymentgrequency','actualpaymentamount','occupationcode','income','netincomeindicator','monthlyincomeindicator'])

                    for user in crifdata:
                        writer.writerow([user.firstname,user.middlename,user.lastname,user.dobddmmyyyy,user.gender,user.panno,user.passportno,user.voteridno,user.dlno,user.rationcardno,user.uid,user.aid,user.telephoneno1,user.telephonetype1,user.telephoneno2,user.telephonetype2,user.telephoneno3,user.telephonetype3,user.telephoneext,user.emailid,user.consumeradd1,user.consumercity1,user.consumerdistrict1,user.consumerstatecode1,user.consumerpincode1,user.consumeraddcategory1,user.consumerresicode1,user.consumeradd2,user.consumercity2,user.consumerdistrict2,user.consumerstatecode2,user.consumerpincode2,user.consumeraddcategory2,user.consumerresicode2,user.membercode,user.membershortname,user.loanacno,user.acnotype,user.ownershipindi,user.loandtddmmyyyy,user.lastemiddmmyyyy,user.closedtddmmyyyy,user.reportdateddmmyyyy,user.loanamount,user.curruntbalance,user.amountoverdue,user.numberofdayspast,user.oldmembercode,user.oldmembershortname,user.oldloanacno,user.oldacnotype,user.oldownershipindi,user.suitfiled,user.writtenoff,user.assetclassification,user.valueofcollateral,user.typeofcollateral,user.creditlimit,user.cashlimit,user.roi,user.repaymenttenure,user.emiamount,user.writtenofamounttotal,user.writtenofamountprin,user.settlementamount,user.paymentgrequency,user.actualpaymentamount,user.occupationcode,user.income,user.netincomeindicator,user.monthlyincomeindicator])

                    message = "CRIF HIMARK CREDIT Score Data being prepared for period..."
                    messages.success(request, message)

                    return response


               
                lastmonth = loginrundate - relativedelta(months=1)
                
                ffromdate = lastmonth.strftime("%Y-%m-01")
                ftodate = lastmonth.strftime("%Y-%m-%d")

                ffromdate = lastmonth.strftime("%Y-%m-01")
                lastdate = calendar.monthrange(lastmonth.year, lastmonth.month)[1]

                ftodate = datetime(lastmonth.year,lastmonth.month, lastdate).strftime("%Y-%m-%d")


               

                context = {'loginlocationcode': loginlocationcode,
                           'loginlocationname': loginlocationname,
                           'loginrundate': loginrundate,
                           'ffromdate': ffromdate,
                           'ftodate': ftodate,
                           }

                return render(request, 'admssadmin/admssadmincrifdata.html', context)


############## LIC DATA EXPORT #############
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminlicdata(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                
                last_month = loginrundate.replace(day=1) - timedelta(1)
                last_month.strftime("%B %Y")

                fromdate = ((last_month.strftime("%Y"))+'-'+(last_month.strftime("%m"))+'-'+'01')
                ffromdate = datetime.strptime(fromdate, "%Y-%m-%d")
                ftodate = last_month

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'ffromdate': ffromdate,
                        'ftodate' : ftodate,
                          }


                if request.method == "POST":
                       ffromdate = request.POST.get('fromdate')
                       ftodate = request.POST.get('todate')
                       fdatatype = request.POST.get('datatype')


                       checkdate = loginrundate - timedelta(days=-60)

                       if fdatatype == 'New Loan':

                           xfromdate = datetime.strptime(ffromdate, "%Y-%m-%d").date()
                           xtodate = datetime.strptime(ftodate, "%Y-%m-%d").date()
                           data = Loanmaster.objects.filter(apploandate__gte=ffromdate, apploandate__lte=ftodate).order_by('locationcode','id')

                       elif fdatatype == 'New Laon & Renew':

                           data = Loanmaster.objects.filter((Q(applifeinsuruptodate__lte=checkdate) | 
                               Q(applifeinsur='N')) & Q(status='A')).order_by('apploandate')


                       Licdata.objects.all().delete()  

                       for x in data:
                           flocationcode = x.locationcode
                           flocationname = x.locationname
                           floanid = x.loanid
                           fappname = x.appname
                           fappgender = x.appgender
                           fappdob = x.appdob
                           fdobdtddmmyyyy = datetime.strftime(x.appdob, "%d-%m-%Y")
                           fcoappname = x.coappname
                           fcoappdob = x.coappdob
                           fcoappdobddmmyyyy = datetime.strftime(x.coappdob, "%d-%m-%Y")
                           floandate = x.apploandate
                           floandtddmmyyyy = datetime.strftime(x.apploandate, "%d-%m-%Y")
                           floantype = x.loantype
                           floanamount = x.apploanamt
                           floantenr = x.apploantenr
                           fbalamount = (x.apploanamt + x.apploanint) - x.apptotalrecamt
                           flifeinsur = x.applifeinsur
                           floanstatus = 'New Loan'
                           
                           if floantenr >= 90:
                               finsurdays = 180
                               mutiple = 2
                           elif floantenr == 360:
                                finsurdays = 180
                                mutiple = 2
                               
                           if flifeinsur=='Y':
                               finsurdays = 180
                               mutiple = 2
                               floanstatus = 'Old Loan'
  
                           fpremium = 0
                           fgst = 0
                           ftotal = (floanamount/1000)*mutiple
                           fdor = loginrundate
                           fdordtddmmyyyy = datetime.strftime(loginrundate, "%d-%m-%Y")
                           flastinsurupto = x.applifeinsuruptodate
                           

                           if x.applifeinsuruptodate is not None:
                               flastinsuruptodtddmmyyyy = datetime.strftime(
                                      x.applifeinsuruptodate, "%d-%m-%Y")
                           else:
                               flastinsuruptodtddmmyyyy=''
                               flastinsurupto = floandate

 
                           lic = Licdata(locationcode=flocationcode,
                                         locationname=flocationname,
                                         loanid=floanid,
                                         appname=fappname,
                                         appdob=fappdob,
                                         dobdtddmmyyyy=fdobdtddmmyyyy,
                                         appgender=fappgender,
                                         coappname=fcoappname,
                                         coappdob=fcoappdob,
                                         coappdobddmmyyyy=fcoappdobddmmyyyy,
                                         loandate=floandate,
                                         loandtddmmyyyy=floandtddmmyyyy,
                                         loantype=floantype,
                                         loanamount=floanamount,
                                         balamount = fbalamount,
                                         loantenr=floantenr,
                                         insurdays=finsurdays,
                                         premium=fpremium,
                                         gst=fgst,
                                         total=ftotal,
                                         lastinsurupto=flastinsurupto,
                                         lastinsuruptodtddmmyyyy=flastinsuruptodtddmmyyyy,
                                         dor=fdor,
                                         dordtddmmyyyy=fdordtddmmyyyy,
                                         loanstatus = floanstatus,
                                             )
                           lic.save()
                           if x.appgender=='Female':
                                      lic = Licdata(locationcode=flocationcode,
                                                    locationname=flocationname,
                                                    loanid=floanid,
                                                    appname=fcoappname,
                                                    appdob=fcoappdob,
                                                    dobdtddmmyyyy=fcoappdobddmmyyyy,
                                                    appgender='Male',
                                                    coappname=fcoappname,
                                                    coappdob=fcoappdob,
                                                    coappdobddmmyyyy=fcoappdobddmmyyyy,
                                                    loandate=floandate,
                                                    loandtddmmyyyy=floandtddmmyyyy,
                                                    loantype=floantype,
                                                    loanamount=floanamount,
                                                    balamount = fbalamount,
                                                    loantenr=floantenr,
                                                    insurdays=finsurdays,
                                                    premium=fpremium,
                                                    gst=fgst,
                                                    total=ftotal,
                                                    lastinsurupto=flastinsurupto,
                                                    lastinsuruptodtddmmyyyy=flastinsuruptodtddmmyyyy,
                                                    dor=fdor,
                                                    dordtddmmyyyy=fdordtddmmyyyy,
                                                    loanstatus = floanstatus
                                                   )
                                      lic.save()    

                        

                       

                       licdata = Licdata.objects.all().order_by('-lastinsurupto').only('loanid','appname','appdob','appgender','loandate','dor','loanamount','loantenr','insurdays','premium','gst','total','coappname','coappdob','balamount','lastinsuruptodtddmmyyyy')

                       response = HttpResponse(content_type='text/csv')
                       response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('licdata')
                       writer = csv.writer(response)
                       writer.writerow(['loanid','appname','appdob','appgender','loandate','dor','loanamount','loantenr','insurdays','premium','gst','total','coappname','coappdob','balamount','lastinsuruptodtddmmyyyy'])

                       for user in licdata:
                          writer.writerow([user.loanid,user.appname,user.appdob,user.appgender,user.loandate,user.dor,user.loanamount,user.loantenr,user.insurdays,user.premium,user.gst,user.total,user.coappname,user.coappdob,user.balamount,user.lastinsuruptodtddmmyyyy])

                       message = "Insurance Data being prepared..."
                       messages.success(request, message)
          
                       return response
                        
                return render(request, 'admssadmin/admssadminlicdata.html' , context)







############## LIC UPDATE #############
#######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminupdatelicdata(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                
                last_month = loginrundate.replace(day=1) - timedelta(1)
                last_month.strftime("%B %Y")

                fromdate = ((last_month.strftime("%Y"))+'-'+(last_month.strftime("%m"))+'-'+'01')
                ffromdate = datetime.strptime(fromdate, "%Y-%m-%d")
                ftodate = last_month

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'ffromdate': ffromdate,
                        'ftodate' : ftodate,
                          }

                from django.core.files.storage import FileSystemStorage

                if request.method == "POST":
                       from pathlib import Path
                       import pandas as pd

                       import os
                       file = request.FILES['myfile']
                       df = pd.read_excel(file)
                       count=0
                       for key,value in df.iterrows():
                           k=1
                           for i in value:
                                if k==1:
                                    floanid = i
                                if k==2:
                                    fdoi = i.strftime("%Y-%m-%d")
                                if k==3:
                                    finsdays = int(i)
                                    finsenddate = datetime.strptime(fdoi,"%Y-%m-%d").date() + timedelta(finsdays)
                                    finsenddate = finsenddate.strftime("%Y-%m-%d")

                                    insmaster = Loanmaster.objects.get(loanid=floanid)
                                    insmaster.applifeinsurdays = finsdays
                                    insmaster.applifeinsurdate = fdoi
                                    insmaster.applifeinsuruptodate = finsenddate
                                    insmaster.save()

                                k=k+1
                           count=count+1
                       message = "Insurance Data "+str(count)+" Records Updated..."
                       messages.success(request, message)
                       return redirect('admssadminupdatelicdata')

                       
                return render(request, 'admssadmin/admssadminupdatelicdata.html' , context)




############# AUDIT MASTER DATA ############
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminauditmasterdata(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:

                if request.method == "POST":
                    ffromdate = request.POST.get('fromdate')
                    ftodate = request.POST.get('todate')

                    #cl = Loanmaster.objects.filter(status='C')
                    #for x in cl:
                    #    ndays = x.apploantenr
                    #    if x.apploandate <= datetime.strptime('19/10/2021', '%d/%m/%Y').date():
                    #        rate = 24.88
                    #    elif x.apploandate >= datetime.strptime('20/10/2021', '%d/%m/%Y').date():
                    #        rate = 21.00

                    #    nint = (x.apploanamt*(rate))/100
                    #    fint=int((nint*ndays)/180)

                    #    x.apploanint = fint
                    #    x.apploandueamt = x.apploanamt + fint
                    #    x.save()


                    Auditloanmaster20252026.objects.all().delete()

                    db = Daybook.objects.filter(date__range=(ffromdate,ftodate),transcd__in=['3010','3011','3012','3019']).distinct('loanid')

                    for x in db:


                        auditmaster = Loanmaster.objects.filter(loanid=x.loanid)



                        for x in auditmaster:
                                flocationcode = x.locationcode
                                flocationname = x.locationname
                                floanid = x.loanid
                                fappname = x.appname
                                fapppresentadd = x.apppresentadd
                                fapppresentaddcity = x.apppresentaddcity
                                fappoccupation = x.appoccupation
                                fappshoplocation = x.appshoplocation
                                fapploanamt = x.apploanamt
                                fapploanint = x.apploanint
                                fapploantenr = x.apploantenr
                                fapploandate = x.apploandate
                                ndays = x.apploantenr
                                fstatus = x.status

                                if x.apploandate <= datetime.strptime('19/10/2021', '%d/%m/%Y').date():
                                    rate = 24.88
                                elif x.apploandate >= datetime.strptime('20/10/2021', '%d/%m/%Y').date():
                                    rate = 21.00

                                rate = 28.00
                                nint = (x.apploanamt*(rate))/100
                                fint = int(((nint*ndays)/180)/1)

                                #fint = fapploanamt * ((24.00/100)/12) * (fapploantenr/30.41)


                                fapploanint = fint

                                fapptotalrecamt = x.apptotalrecamt
                                fappprinrecamt = x.appprinrecamt
                                fappintrecamt = x.appintrecamt
                                fapploantype = x.loantype
                                if x.apploandate < datetime.strptime('20/01/2021', '%d/%m/%Y').date() and x.loantype == 'GROUP':
                                    fapploantype = 'INDIVIDUAL'

                                fapploansettlementdate = x.apploansettlementdate
                                fapplastemidepdate = x.applastemidepdate


                                amount = int(fapploanamt)
                                ndays = int(fapploantenr)


                                fapploandueamt = fapploanamt + fapploanint
                        

                                if fappintrecamt > fapploanint:
                                    fappintrecamt = fapploanint

                                if fappprinrecamt > fapploanamt:
                                    fappprinrecamt = fapploanamt

                                fappprinbalamt = fapploanamt - fappprinrecamt
                                fappintbalamt = fapploanint - fappintrecamt

                                fapptotalbalamt = fappprinbalamt + fappintbalamt
                                
                                ######### 2019 - 2020 ##########

                                ffromtmp = '01/04/2019'
                                ftotmp = '31/03/2020'

                                ffromtmp = datetime.strptime('01/04/2019', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2020', '%d/%m/%Y')

                                p20192020 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011","3019"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20192020 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20192020 = p20192020.get("totamt")
                                fappintrecamt20192020 = i20192020.get("totamt")

                                pbank20192020 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011","3019"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20192020 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20192020bank = pbank20192020.get("totamt")
                                fappintrecamt20192020bank = ibank20192020.get("totamt")

                                ######### 2020 - 2021 ##########

                                ffromtmp = '01/04/2020'
                                ftotmp = '31/03/2021'

                                ffromtmp = datetime.strptime('01/04/2020', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2021', '%d/%m/%Y')

                                p20202021 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011","3019"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20202021 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20202021 = p20202021.get("totamt")
                                fappintrecamt20202021 = i20202021.get("totamt")


                                pbank20202021 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011","3019"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20202021 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20202021bank = pbank20202021.get("totamt")
                                fappintrecamt20202021bank = ibank20202021.get("totamt")

                                ######### 2021 - 2022 ##########

                                ffromtmp = '01/04/2021'
                                ftotmp = '31/03/2022'

                                ffromtmp = datetime.strptime('01/04/2021', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2022', '%d/%m/%Y')

                                p20212022 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20212022 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20212022 = p20212022.get("totamt")
                                fappintrecamt20212022 = i20212022.get("totamt")

                                pbank20212022 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20212022 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20212022bank = pbank20212022.get("totamt")
                                fappintrecamt20212022bank = ibank20212022.get("totamt")

                                ######### 2022 - 2023 ##########

                                ffromtmp = '01/04/2022'
                                ftotmp = '31/03/2023'

                                ffromtmp = datetime.strptime('01/04/2022', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2023', '%d/%m/%Y')

                                p20222023 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20222023 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                #fappprinrecamt20222023 = p20222023.get("totamt")
                                #fappintrecamt20222023 = i20222023.get("totamt")

                                fappprinrecamt20222023 = p20222023.get("totamt")
                                fappintrecamt20222023 = i20222023.get("totamt")

                                fappprinrecamt20222023 = fappprinrecamt20222023 * .8721
                                fappintrecamt20222023 = fappintrecamt20222023 * .8691




                                pbank20222023 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20222023 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20222023bank = pbank20222023.get("totamt")
                                fappintrecamt20222023bank = ibank20222023.get("totamt")


                                ######### 2023 - 2024 ##########

                                ffromtmp = '01/04/2023'
                                ftotmp = '31/03/2024'

                                ffromtmp = datetime.strptime('01/04/2023', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2024', '%d/%m/%Y')

                                p20232024 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20232024 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                ####################################################
                                fappprinrecamt20232024 = p20232024.get("totamt")*.950846
                                #.86485
                                ####################################################
                                fappintrecamt20232024 = i20232024.get("totamt")*.6924857
                                #.80248599

                                pbank20232024 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20232024 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20232024bank = pbank20232024.get("totamt")
                                fappintrecamt20232024bank = ibank20232024.get("totamt")



                                ######### 2024 - 2025 ##########

                                ffromtmp = '01/04/2024'
                                ftotmp = '31/03/2025'

                                ffromtmp = datetime.strptime('01/04/2024', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2025', '%d/%m/%Y')

                                p20242025 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20242025 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                ####################################################
                                fappprinrecamt20242025 = p20242025.get("totamt")
                                #*1.011846
                            
                                ####################################################
                                fappintrecamt20242025 = i20242025.get("totamt")
                                #.711075

                                pbank20242025 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20242025 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20242025bank = pbank20242025.get("totamt")
                                fappintrecamt20242025bank = ibank20242025.get("totamt")


                                ######### 2025 - 2026 ##########

                                ffromtmp = '01/04/2025'
                                ftotmp = '31/03/2026'

                                ffromtmp = datetime.strptime('01/04/2025', '%d/%m/%Y')
                                ftotmp = datetime.strptime('31/03/2026', '%d/%m/%Y')

                                p20252026 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                i20252026 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                ####################################################
                                fappprinrecamt20252026 = p20252026.get("totamt")*0.9200011
                                #.86485
                                ####################################################
                                fappintrecamt20252026 = i20252026.get("totamt")*1.1969115
                                #.80248599

                                pbank20252026 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3011"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))
                                ibank20252026 = Daybook.objects.filter(date__range=(ffromtmp, ftotmp), transcd__in=["3012"], mode__icontains='BANK', loanid=floanid).aggregate(totalac=Coalesce(Count('transid'), 0), totamt=Coalesce(Sum('amount'), 0))

                                fappprinrecamt20252026bank = pbank20252026.get("totamt")
                                fappintrecamt20252026bank = ibank20252026.get("totamt")



                                if fapploantype == "INDIVIDUAL":
                                    if fapploandate <= datetime.strptime('19/10/2021', '%d/%m/%Y').date():

                                        fapploanint = int(fapploanint/1.50)

                                        if fappintrecamt20192020 > 0:
                                            fappintrecamt20192020 = int(fappintrecamt20192020/1.50)

                                        if fappintrecamt20192020bank > 0:
                                            fappintrecamt20192020bank = int(fappintrecamt20192020bank/1.50)

                                        if fappintrecamt20202021 > 0:
                                            fappintrecamt20202021 = int(fappintrecamt20202021/1.50)

                                        if fappintrecamt20202021bank > 0:
                                            fappintrecamt20202021bank = int(fappintrecamt20202021bank/1.50)

                                        if fappintrecamt20212022 > 0:
                                            fappintrecamt20212022 = int(fappintrecamt20212022/1.50)

                                        if fappintrecamt20212022bank > 0:
                                            fappintrecamt20212022bank = int(fappintrecamt20212022bank/1.50)

                                        if fappintrecamt20212022 > 0:
                                            fappintrecamt20212022 = int(fappintrecamt20212022/1.50)

                                        if fappintrecamt20212022bank > 0:
                                            fappintrecamt20212022bank = int(fappintrecamt20212022bank/1.50)


                                    elif fapploandate >= datetime.strptime('20/10/2021', '%d/%m/%Y').date():

                                        fapploanint = int(fapploanint/1.56)

                                        if fappintrecamt20212022 > 0:
                                            fappintrecamt20212022 = int(fappintrecamt20212022/1.56)

                                        if fappintrecamt20212022bank > 0:
                                            fappintrecamt20212022bank = int(fappintrecamt20212022bank/1.56)

                                elif fapploantype == "GROUP":

                                    if fappintrecamt20202021 > 0:

                                        fappintrecamt20202021 = int(fappintrecamt20202021)
                                        fappintrecamt20202021bank = int(fappintrecamt20202021bank)
                                    
                                    if fappintrecamt20212022 > 0:

                                        fappintrecamt20212022 = int(fappintrecamt20212022)
                                        fappintrecamt20212022bank = int(fappintrecamt20212022bank)




                                fapptotalrecamt20192020 = 0
                                fapptotalrecamt20202021 = 0
                                fapptotalrecamt20212022 = 0
                                fapptotalrecamt20222023 = 0
                                fapptotalrecamt20232024 = 0
                                fapptotalrecamt20242025 = 0
                                fapptotalrecamt20252026 = 0

                                fapptotalrecamt20192020 = int(fappprinrecamt20192020) + int(fappintrecamt20192020)
                                fapptotalrecamt20202021 = int(fappprinrecamt20202021) + int(fappintrecamt20202021)
                                fapptotalrecamt20212022 = int(fappprinrecamt20212022) + int(fappintrecamt20212022)
                                fapptotalrecamt20222023 = int(fappprinrecamt20222023) + int(fappintrecamt20222023)
                                fapptotalrecamt20232024 = int(fappprinrecamt20232024) + int(fappintrecamt20232024)
                                fapptotalrecamt20242025 = int(fappprinrecamt20242025) + int(fappintrecamt20242025)
                                fapptotalrecamt20252026 = int(fappprinrecamt20252026) + int(fappintrecamt20252026)


                                fappdueamt20192020 = 0
                                fappdueamt20202021 = 0
                                fappdueamt20212022 = 0
                                fappdueamt20222023 = 0
                                fappdueamt20232024 = 0
                                fappdueamt20242025 = 0
                                fappdueamt20252026 = 0



                                fappdueamt20192020 = fapptotalrecamt20192020
                                fappdueamt20202021 = fapptotalrecamt20202021
                                fappdueamt20212022 = fapptotalrecamt20212022
                                fappdueamt20222023 = fapptotalrecamt20222023
                                fappdueamt20232024 = fapptotalrecamt20232024
                                fappdueamt20242025 = fapptotalrecamt20242025
                                fappdueamt20252026 = fapptotalrecamt20252026


                                if fappprinrecamt20192020 > 0:
                                     fappprinrecamt20192020 = fappprinrecamt20192020 * .2

                                if fappintrecamt20192020 > 0:
                                     fappintrecamt20192020 = fappintrecamt20192020 * .7
                                     
                                if fappprinrecamt20202021 > 0:
                                     fappprinrecamt20202021 = fappprinrecamt20202021 * .2

                                if fappintrecamt20202021 > 0:
                                     fappintrecamt20202021 = fappintrecamt20202021 * .7

                                if fappprinrecamt20212022 > 0:
                                     fappprinrecamt20212022 = fappprinrecamt20212022 * .2

                                if fappintrecamt20212022 > 0:
                                     fappintrecamt20212022 = fappintrecamt20212022 * .7

                                if fappprinrecamt20222023 > 0:
                                     fappprinrecamt20222023 = fappprinrecamt20222023 * .2

                                if fappintrecamt20222023 > 0:
                                     fappintrecamt20222023 = fappintrecamt20222023 * .7

                                if fappprinrecamt20232024 > 0:
                                     fappprinrecamt20232024 = fappprinrecamt20232024 * .2

                                if fappintrecamt20232024 > 0:
                                     fappintrecamt20232024 = fappprinrecamt20232024 * .7

                                if fappprinrecamt20242025 > 0:
                                     fappprinrecamt20242025  = fappprinrecamt20242025 * .2

                                if fappintrecamt20242025 > 0:
                                     fappintrecamt20242025 = fappintrecamt20242025 * .7




                                if fappprinrecamt20192020 <= 0:
                                     fappprinrecamt20192020 = 0
                                if fappintrecamt20192020 <= 0:
                                     fappintrecamt20192020 = 0
                                     

                                if fappprinrecamt20202021 <= 0:
                                     fappprinrecamt20202021 = 0
                                if fappintrecamt20202021 <= 0:
                                     fappintrecamt20202021 = 0



                                if fappprinrecamt20212022 <= 0:
                                     fappprinrecamt20212022 = 0
                                if fappintrecamt20212022 <= 0:
                                     fappintrecamt20212022 = 0

                                if fappprinrecamt20222023 <= 0:
                                     fappprinrecamt20222023 = 0
                                if fappintrecamt20222023 <= 0:
                                     fappintrecamt20222023 = 0

                                if fappprinrecamt20232024 <= 0:
                                     fappprinrecamt20232024 = 0
                                if fappintrecamt20232024 <= 0:
                                     fappintrecamt20232024 = 0

                                if fappprinrecamt20242025 <= 0:
                                     fappprinrecamt20242025 = 0
                                if fappintrecamt20242025 <= 0:
                                     fappintrecamt20242025 = 0


                                fapptotalrecamt20192020 = fappprinrecamt20192020 + fappintrecamt20192020
                                fapptotalrecamt20202021 = fappprinrecamt20202021 + fappintrecamt20202021
                                fapptotalrecamt20212022 = fappprinrecamt20212022 + fappintrecamt20212022
                                fapptotalrecamt20222023 = fappprinrecamt20222023 + fappintrecamt20222023
                                fapptotalrecamt20232024 = fappprinrecamt20232024 + fappintrecamt20232024
                                fapptotalrecamt20242025 = fappprinrecamt20242025 + fappintrecamt20242025
                                fapptotalrecamt20252026 = fappprinrecamt20252026 + fappintrecamt20252026



                                fappprinrecamt = fappprinrecamt20192020 + fappprinrecamt20202021 + fappprinrecamt20212022 + fappprinrecamt20222023 + fappprinrecamt20232024 + fappprinrecamt20242025 + fappprinrecamt20252026 
                                fappintrecamt = fappintrecamt20192020 + fappintrecamt20202021 + fappintrecamt20212022 + fappintrecamt20222023 + fappintrecamt20232024 + fappintrecamt20242025 + fappintrecamt20252026
                                fapptotalrecamt = fappprinrecamt + fappintrecamt


 
                                fappprinbalamt = fapploanamt - (fappprinrecamt20192020 + fappprinrecamt20202021 + fappprinrecamt20212022 + fappprinrecamt20222023 + fappprinrecamt20232024 + fappprinrecamt20242025 + fappprinrecamt20252026) 

                                fappintbalamt = (fapploanint - fappintrecamt)

                                fappprinbalamt = fappprinbalamt * 1.6332
                                     
                                fapptotalbalamt = fappprinbalamt + fappintbalamt


                                if fappintbalamt < 0:
                                    fappintbalamt = 0
                                if fappprinbalamt < 0:
                                    fappprinbalamt = 0


                                if fstatus == 'C' and fapploanamt < 50000: 

                                    fappprinrecamt = fappprinrecamt20192020 + fappprinrecamt20202021 + fappprinrecamt20212022 + fappprinrecamt20222023 + fappprinrecamt20232024 + fappprinrecamt20242025 + fappprinrecamt20252026 
                                    fappintrecamt = fappintrecamt20192020 + fappintrecamt20202021 + fappintrecamt20212022 + fappintrecamt20222023 + fappintrecamt20232024 + fappintrecamt20242025 + fappintrecamt20252026
                                    fapptotalrecamt = fappprinrecamt + fappintrecamt


                                    fapploandueamt = fapptotalrecamt
                                    fapploanamt = fappprinrecamt
                                    fapploanint = fappintrecamt

                                    fappprinbalamt = 0
                                    fappintbalamt = 0
                                    fapptotalbalamt = 0


            

                                audit = Auditloanmaster20252026(locationcode=flocationcode,
                                                                    locationname=flocationname,
                                                                    appname=fappname,
                                                                    loanid=floanid,
                                                                    apppresentadd=fapppresentadd,
                                                                    apppresentaddcity=fapppresentaddcity,
                                                                    appoccupation=fappoccupation,
                                                                    apploandate=fapploandate,
                                                                    apploansettlementdate=fapploansettlementdate,
                                                                    applastemidepdate=fapplastemidepdate,
                                                                    appprindueamt=fapploanamt,
                                                                    appintdueamt=fapploanint,
                                                                    apptotaldueamt=(fapploanamt+fapploanint),
                                                                    appprinrecamt20192020=fappprinrecamt20192020,
                                                                    appintrecamt20192020=fappintrecamt20192020,
                                                                    apptotalrecamt20192020=fapptotalrecamt20192020,
                                                                    appprinrecamt20202021=fappprinrecamt20202021,
                                                                    appintrecamt20202021=fappintrecamt20202021,
                                                                    apptotalrecamt20202021=fapptotalrecamt20202021,
                                                                    appprinrecamt20212022=fappprinrecamt20212022,
                                                                    appintrecamt20212022=fappintrecamt20212022,
                                                                    apptotalrecamt20212022=fapptotalrecamt20212022,
                                                                    appprinrecamt20222023=fappprinrecamt20222023,
                                                                    appintrecamt20222023=fappintrecamt20222023,
                                                                    apptotalrecamt20222023=fapptotalrecamt20222023,
                                                                    appprinrecamt20232024=fappprinrecamt20232024,
                                                                    appintrecamt20232024=fappintrecamt20232024,
                                                                    apptotalrecamt20232024=fapptotalrecamt20232024,
                                                                    appprinrecamt20242025=fappprinrecamt20242025,
                                                                    appintrecamt20242025=fappintrecamt20242025,
                                                                    apptotalrecamt20242025=fapptotalrecamt20242025,
                                                                    appprinrecamt20252026=fappprinrecamt20252026,
                                                                    appintrecamt20252026=fappintrecamt20252026,
                                                                    apptotalrecamt20252026=fapptotalrecamt20252026,
                                                                    appdueamt20192020=fappdueamt20192020,
                                                                    appdueamt20202021=fappdueamt20202021,
                                                                    appdueamt20212022=fappdueamt20212022,
                                                                    appdueamt20222023=fappdueamt20222023,
                                                                    appdueamt20232024=fappdueamt20232024,
                                                                    appdueamt20242025=fappdueamt20242025,
                                                                    appdueamt20252026=fappdueamt20252026,                                                                    
                                                                    appprinrecamt=fappprinrecamt,
                                                                    appintrecamt=fappintrecamt,
                                                                    apptotalrecamt=fapptotalrecamt,
                                                                    appprinbalamt=fappprinbalamt,
                                                                    appintbalamt=fappintbalamt,
                                                                    apptotalbalamt=fapptotalbalamt,
                                                                    status=fstatus)
                                audit.save()
                            



                    auditdata = Auditloanmaster20252026.objects.all().order_by('id').only('loanid','appname','apppresentadd','apppresentaddcity','appoccupation','appprindueamt','appintdueamt','apptotaldueamt','appprinrecamt20192020','appintrecamt20192020','apptotalrecamt20192020','appprinrecamt20202021','appintrecamt20202021','apptotalrecamt20202021','appprinrecamt20212022','appintrecamt20212022','apptotalrecamt20212022','appprinrecamt20222023','appintrecamt20222023','apptotalrecamt20222023','appprinrecamt20232024','appintrecamt20232024','apptotalrecamt20232024','appprinrecamt20242025','appintrecamt20242025','apptotalrecamt20242025','appprinrecamt20252026','appintrecamt20252026','apptotalrecamt20252026','appprinrecamt','appintrecamt','apptotalbalamt','appprinbalamt','appintbalamt','apptotalbalamt','apploandate','status')

                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('auditdata')
                    writer = csv.writer(response)
                    writer.writerow(['loanid','appname','apppresentadd','apppresentaddcity','appoccupation','appprindueamt','appintdueamt','apptotaldueamt','appprinrecamt20192020','appintrecamt20192020','apptotalrecamt20192020','appprinrecamt20202021','appintrecamt20202021','apptotalrecamt20202021','appprinrecamt20212022','appintrecamt20212022','apptotalrecamt20212022','appprinrecamt20222023','appintrecamt20222023','apptotalrecamt20222023','appprinrecamt20232024','appintrecamt20232024','apptotalrecamt20232024','appprinrecamt20242025','appintrecamt20242025','apptotalrecamt20242025','appprinrecamt20252026','appintrecamt20252026','apptotalrecamt20252026','appprinrecamt','appintrecamt','apptotalbalamt','appprinbalamt','appintbalamt','apptotalbalamt','apploandate','status'])

                    for user in auditdata:
                        writer.writerow([user.loanid,user.appname,user.apppresentadd,user.apppresentaddcity,user.appoccupation,user.appprindueamt,user.appintdueamt,user.apptotaldueamt,user.appprinrecamt20192020,user.appintrecamt20192020,user.apptotalrecamt20192020,user.appprinrecamt20202021,user.appintrecamt20202021,user.apptotalrecamt20202021,user.appprinrecamt20212022,user.appintrecamt20212022,user.apptotalrecamt20212022,user.appprinrecamt20222023,user.appintrecamt20222023,user.apptotalrecamt20222023,user.appprinrecamt20232024,user.appintrecamt20232024,user.apptotalrecamt20232024,user.appprinrecamt20242025,user.appintrecamt20242025,user.apptotalrecamt20242025,user.appprinrecamt20252026,user.appintrecamt20252026,user.apptotalrecamt20252026,user.appprinrecamt,user.appintrecamt,user.apptotalrecamt,user.appprinbalamt,user.appintbalamt,user.apptotalbalamt,user.apploandate,user.status])

                    message = "AUDIT Loan Master Data Prepared..."
                    messages.success(request, message)
                    
                    return response


                    return HttpResponseRedirect('/admssadminauditmasterdata/')

                ffromdate = datetime(2025, 4, 1)
                ftodate = datetime(2026, 3, 31)

                context = {'loginlocationcode': loginlocationcode,
                           'loginlocationname': loginlocationname,
                           'loginrundate': loginrundate,
                           'ffromdate': ffromdate,
                           'ftodate': ftodate,
                           }

                return render(request, 'admssadmin/admssadminauditloanmaster.html', context)





############ CHANGE TENURE ##########
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminchangetenure(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                

                fbranch = Locationlogin.objects.values('locationcode','locationname').all().distinct().order_by('locationname')   

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        'fbranch':fbranch,
                          }



                if request.method == "POST":

                       flocation = request.POST.get('locationcode')
                       nname = Loanmaster.objects.filter(locationcode=flocation,status='A').order_by('appname','apploandate')
                       fbranch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 

                       flocationcode =  fbranch[0].locationcode
                       flocationname = fbranch[0].locationname

                       context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'flocationcode':flocationcode,
                                      'flocationname':flocationname,
                                      'nname':nname,

                                      }

                       return render(request, 'admssadmin/admssadminchangetenureget.html', context)
                        
                return render(request, 'admssadmin/admssadminchangetenure.html' , context)




############ CHANGE TENURE GET ##########
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminchangetenureget(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                



                if request.method == "POST":

                       flocation = request.POST.get('locationcode')
                       fbranch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 
                       fapploanid = request.POST.get('loanidname')

                       flocationcode =  fbranch[0].locationcode
                       flocationname = fbranch[0].locationname

                       loanmast = Loanmaster.objects.get(locationcode=flocation,loanid=fapploanid)
                       alldays = Loanscheme.objects.filter(loandays__lte=365).distinct('loandays').order_by('loandays')
                       allfreq = Loanscheme.objects.filter().distinct('emifreq').order_by('emifreq')    


                       floantype = loanmast.loantype
                       if floantype == "INDIVIDUAL":
                            allfreq = Loanscheme.objects.filter(emifreq__in=['DAILY','WEEKLY','MONTHLY']).distinct('emifreq').order_by('emifreq')    
                       elif floantype == "GROUP":
                            allfreq = Loanscheme.objects.filter(emifreq__in=['FORTNIGHTLY']).distinct('emifreq').order_by('emifreq')   

                       fapploanid = loanmast.loanid
                       fappname = loanmast.appname
                       fapploanemi = loanmast.apploanemi
                       fapploandate = loanmast.apploandate
                       fapplastemidepdate = loanmast.applastemidepdate
                       fapplastemidepday = ''
                       if fapplastemidepdate is not None:
                           fapplastemidepday = loanmast.applastemidepdate.strftime('%A')


                       fappemiduedate = loanmast.appemiduedate
                       ftotaldue = loanmast.apploanamt + loanmast.apploanint
                       fapptotalrecamt = loanmast.apptotalrecamt
                       fapploanamt = loanmast.apploanamt
                       fappoccupation = loanmast.appoccupation
                       fappshoplocation = loanmast.appshoplocation
                       frpersoncode = loanmast.rpersoncode
                       frpersonname = loanmast.rpersonname
                       femiday = loanmast.colldaychar
                       floantenr = loanmast.apploantenr
                       fappemifreq = loanmast.appemifreq

                       loginlocationcode = flocationcode


                       fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)





                       context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'flocationcode':flocationcode,
                                      'flocationname':flocationname,
                                      'fapploanid': fapploanid,
                                      'fappname':fappname,
                                      'fapploanemi':fapploanemi,
                                      'fapplastemidepdate':fapplastemidepdate,
                                      'fapplastemidepday':fapplastemidepday,
                                      'ftotaldue':ftotaldue,
                                      'fapptotalrecamt':fapptotalrecamt,
                                      'fapploanamt':fapploanamt,
                                      'fappoccupation':fappoccupation,
                                      'fappshoplocation':fappshoplocation,
                                      'frpersoncode':frpersoncode,
                                      'femiday':femiday,
                                      'floantenr':floantenr,
                                      'floantype':floantype,
                                      'fappemifreq':fappemifreq,
                                      'fapploandate':fapploandate,
                                      'fapptotalrecamt':fapptotalrecamt,
                                      'allfreq':allfreq,
                                      'alldays':alldays,

                                      }

                       return render(request, 'admssadmin/admssadminchangetenurecommit.html', context)






############ CHANGE TENURE COMMIT ##########
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminchangetenurecommit(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                



                if request.method == "POST":

                       flocation = request.POST.get('locationcode')
                       fbranch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 
                       fapploanid = request.POST.get('loanidname')
                       fapploantenr = request.POST.get('apploantenr')
                       fappemifreq = request.POST.get('appemifreq')

                       flocationcode =  fbranch[0].locationcode
                       flocationname = fbranch[0].locationname

                       loanmast = Loanmaster.objects.get(locationcode=flocation,loanid=fapploanid)
                       fapploantype = loanmast.loantype
                       fappname = loanmast.appname

                       loanmast.apploantenr = fapploantenr
                       loanmast.appemifreq = fappemifreq


                       amount = loanmast.apploanamt
              
                       ndays = int(fapploantenr)


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

                       loanmast.apploanemiprin = fapploanemiprin
                       loanmast.apploanemiint = fapploanemiint
                       loanmast.appemifreq = fappemifreq
                       loanmast.apploanemi = fapploanemi
                       loanmast.apploanint = fint
                       loanmast.apploandueamt =  loanmast.apploanamt + fint

                       loanmast.save()

                       message = "New Loan ID "+fapploanid+" / "+fappname+" / "+fapploantenr+" / "+fappemifreq+" / Changed Successfully."
                       messages.success(request, message)
                       return HttpResponseRedirect('/admssadminchangetenure/')


############ SEARCH ENTRY IN DATA ##########
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminsearch(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                
                last_month = loginrundate.replace(day=1) - timedelta(1)
                last_month.strftime("%B %Y")

                ffromdate = '2020-05-01'
                ftodate = '2020-05-31'

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                          }


                if request.method == "POST":
                       fdb = request.POST.get('db')
                       fsearchtext = request.POST.get('searchtext')

                       if fdb == 'DAYBOOK':
                                               
                            searchdb = Daybook.objects.filter(Q(appname__contains=fsearchtext) | Q(amount__contains=fsearchtext) | Q(narration__contains=fsearchtext)).order_by('transid')

                       #loanledger = Loantrans.objects.filter(Q(date__lte=ftodate) & Q(date__gte=ffromdate)).select_related('master')


                       context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'fdb':fdb,
                                      'fsearchtext':fsearchtext,
                                      'searchdb':searchdb,
                                      }

                       return render(request, 'admssadmin/admssadminsearchshow.html', context)
                        
                return render(request, 'admssadmin/admssadminsearch.html' , context)



############  UPDATE  ##########
################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminupdate(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                

                fbranch = Locationlogin.objects.values('locationcode','locationname').all().distinct().order_by('locationname')   

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        'fbranch':fbranch,
                          }


                if request.method == "POST":
                       ftypeentry = request.POST.get('typeentry')
                       flocation = request.POST.get('locationcode')
                       ftypeaction = request.POST.get('typeaction')



                       branch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 

                       flocationcode =  branch[0].locationcode
                       flocationname = branch[0].locationname

                           
                       allbank = Opclcashbank.objects.filter(locationcode=flocationcode,date=loginrundate,defaultbank='Y')
                       clcash = allbank[0].clcash
                       clbank = allbank[0].clbank


                           

                       context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'flocationcode':flocationcode,
                                      'flocationname':flocationname,
                                      'ftypeentry':ftypeentry,
                                      'ftypeaction':ftypeaction,
                                      'flocation':flocation,
                                      'allbank':allbank,
                                      'clcash':clcash,
                                      'clbank':clbank,

                                        }

                       return render(request, 'admssadmin/admssadminupdateget.html', context)
                        
                return render(request, 'admssadmin/admssadminupdate.html' , context)


############  UPDATE COMMIT  ##########
#######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminupdatecommit(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                


                if request.method == "POST":
                       ftypeentry = request.POST.get('typeentry')
                       flocation = request.POST.get('locationcode')
                       ftypeaction = request.POST.get('typeaction')

                       famount = request.POST.get('amount')
                       fbankac = request.POST.get('bankac')

                       branch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 

                       flocationcode =  branch[0].locationcode
                       flocationname = branch[0].locationname
                           
                       if ftypeentry == "BANK":
                            allbank = Opclcashbank.objects.get(locationcode=flocationcode,date=loginrundate,bankac=fbankac)
                            clcash = allbank.clcash
                            clbank = allbank.clbank

                            if int(famount) > clbank:
                                pass
                            else:
                                if ftypeaction == "D":
                                    allbank.clbank = allbank.clbank - int(famount)
                                    allbank.save()
                                elif ftypeaction == "I":
                                    allbank.clbank = allbank.clbank + int(famount)
                                    allbank.save()

                    
                       elif ftypeentry == "CASH":
                            allcash = Opclcashbank.objects.filter(locationcode=flocationcode,date=loginrundate)
                            clcash = allcash[0].clcash

                            if int(famount) > clcash:
                                pass
                            else:
                                if ftypeaction == "D":
                                    for x in allcash:
                                        x.clcash = x.clcash - int(famount)
                                        x.save()
                                elif ftypeaction == "I":    
                                    for x in allcash:
                                        x.clcash = x.clcash + int(famount)
                                        x.save()
                       

                       message = "Update /"+flocationname+"/"+ftypeentry+"/"+ftypeaction+"/"+famount +"/Successfully..."
                       success = True

                       messages.success(request, message)
                       return HttpResponseRedirect('/admssadminupdate/')



############ DELETE EMI  ##########
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeleteemi(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                

                fdateofentry = date.strftime(loginrundate, "%Y-%m-%d")
                fbranch = Locationlogin.objects.values('locationcode','locationname').all().distinct().order_by('locationname')   


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        'fdateofentry':fdateofentry,
                        'fbranch':fbranch,
                          }


                if request.method == "POST":
                        fdateofentry = request.POST.get('dateofentry')
                        flocation = request.POST.get('locationcode')

                        branch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 

                        flocationcode =  branch[0].locationcode
                        flocationname = branch[0].locationname

                        emientry = Daybook.objects.filter(date=fdateofentry, locationcode=flocation, transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname','transid','appname','date','loanid','mode').annotate(amount=Coalesce(Sum('amount'),0))

                        context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'fdateofentry':fdateofentry,
                                      'flocationcode':flocationcode,
                                      'flocationname':flocationname,
                                      'emientry':emientry,
                                    }

                        return render(request, 'admssadmin/admssadmindeleteemiget.html', context)
                        
                return render(request, 'admssadmin/admssadmindeleteemi.html' , context)



############ DELETE EMI GET ##########
######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeleteemiget(request,deletedata_transid):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['H']):
        return HttpResponseRedirect('/login')
    else:



        
            deletedata=Daybook.objects.filter(transid=deletedata_transid)
            deleteloantrans=Loantrans.objects.filter(transid=deletedata_transid)


            floanid = deletedata[0].loanid
            ftransid = deletedata[0].transid
            fmode = deletedata[0].mode
            fappbankac = deletedata[0].bankac
            fappname =  deletedata[0].appname

            if deletedata[0].transcd == '3011' or deletedata[0].transcd == '3012' or deletedata[0].transcd == '3013' or deletedata[0].transcd == '3019':
                ftypeentry = 'EMI'
                fdateofentry = deletedata[0].date
                fdateofentry = date.strftime(fdateofentry, "%Y-%m-%d")




            fnoofrecorddaybok = Daybook.objects.filter(transid=deletedata_transid).count()
            fnoofrecordloantrans = Loantrans.objects.filter(transid=deletedata_transid).count()

            daybookentried = Daybook.objects.filter(transid=deletedata_transid)
            loantransentries = Loantrans.objects.filter(transid=deletedata_transid)

            loanmast = Loanmaster.objects.get(loanid=floanid)

            emientry = Daybook.objects.filter(transid=ftransid, locationcode='1001', transcd__in=['3011','3012','3019','3013']).values('locationcode','locationname','transid','appname','date','loanid','mode').aggregate(amount=Coalesce(Sum('amount'),0))

            famount = emientry.get("amount")

            context = {'loginlocationcode': loginlocationcode,
                       'loginlocationname': loginlocationname,
                       'loginrundate': loginrundate,
                       'currdate':currdate,
                       'floanid':floanid,
                       'ftransid':ftransid,
                       'ftypeentry':ftypeentry,
                       'fdateofentry':fdateofentry,
                       'fnoofrecorddaybok':fnoofrecorddaybok,
                       'fnoofrecordloantrans':fnoofrecordloantrans,
                       'daybookentried':daybookentried,
                       'loantransentries':loantransentries,
                       'fappname':fappname,
                       'famount':famount,
                       'fmode':fmode,
                       'deletedata':deletedata,
                       'deleteloantrans':deleteloantrans,

                        }


            return render(request, 'admssadmin/admssadmindeleteemicommit.html', context)





############ DELETE EMI COMMIT ##########
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeleteemicommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['H']):
        return HttpResponseRedirect('/login')
    else:

            floanid = request.POST.get('loanid')
            ftransid = request.POST.get('transid')

            deletedata=Daybook.objects.filter(transid=ftransid)

            flocationcode = deletedata[0].locationcode
            floanid = deletedata[0].loanid
            ftransid = deletedata[0].transid
            fmode = deletedata[0].mode
            fappbankac = deletedata[0].bankac




            fprinamt = 0
            fintamt = 0
            flatefee = 0
            fextraprin = 0

            for a in deletedata:
                if a.transcd == '3011':
                    fprinamt = a.amount

                if a.transcd == '3012':
                    fintamt = a.amount

                if a.transcd == '3013':
                    flatefee = a.amount

                if a.transcd == '3019':
                    fextraprin = a.amount

            fnoofrecorddaybook = Daybook.objects.filter(transid=ftransid).count()
            fnoofrecordloantrans = Loantrans.objects.filter(transid=ftransid).count()

            Daybook.objects.filter(transid=ftransid).delete()
            Loantrans.objects.filter(transid=ftransid).delete()


            loanmast = Loanmaster.objects.get(loanid=floanid)
            loantrantmp = Loantrans.objects.filter(loanid=floanid).order_by("-id")
            fapplastemidepdate = loantrantmp[0].date


            loanmast.applastemidepdate = fapplastemidepdate

            if loanmast.appemifreq == 'WEEKLY':
                loanmast.appemiduedate = loanmast.appemiduedate - timedelta(7)
            elif loanmast.appemifreq == 'DAILY':
                loanmast.appemiduedate = loanmast.appemiduedate - timedelta(1)
            elif loanmast.appemifreq == 'FORTNIGHTLY':
                loanmast.appemiduedate = loanmast.appemiduedate - timedelta(15)
            elif loanmast.appemifreq == 'MONTHLY':
                loanmast.appemiduedate = loanmast.appemiduedate - timedelta(30)

            famount = (fprinamt + fintamt + flatefee + fextraprin)

            loanmast.apptotalrecamt = loanmast.apptotalrecamt - famount
            loanmast.appprinrecamt =  loanmast.appprinrecamt - (fprinamt + fextraprin)
            loanmast.appintrecamt = loanmast.appintrecamt - fintamt
            loanmast.applatefeeamt = loanmast.applatefeeamt - flatefee   
            loanmast.save()

            if fmode == 'CASH':
                allcash = Opclcashbank.objects.filter(locationcode=flocationcode,date=loginrundate)
        
                for all in allcash:
                    all.clcash = all.clcash - famount
                    all.save()

            if fmode == 'BANK':
                allbank = Opclcashbank.objects.get(locationcode=flocationcode,bankac=fappbankac,date=loginrundate)
                allbank.clbank=allbank.clbank - famount
                allbank.save()


            message = "EMI Deleted , Daybook record " + str(fnoofrecorddaybook) + " / Loantrans record " + str(fnoofrecordloantrans)+" / "+"Rs."+str(famount)+" / Deleted Succesfully through "+fmode

            messages.success(request, message)
            return HttpResponseRedirect('/admssadmindeleteemi/')


############ DELETE PAYMENT ##########
######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeletepayment(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:
                

                fdateofentry = date.strftime(loginrundate, "%Y-%m-%d")
                fbranch = Locationlogin.objects.values('locationcode','locationname').all().distinct().order_by('locationname')   


                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                        'fdateofentry':fdateofentry,
                        'fbranch':fbranch,
                          }


                if request.method == "POST":
                       fdateofentry = request.POST.get('dateofentry')
                       flocation = request.POST.get('locationcode')

                       branch = Locationlogin.objects.filter(locationcode=flocation).distinct().order_by('locationname') 

                       flocationcode =  branch[0].locationcode
                       flocationname = branch[0].locationname


                      

                       #values = Blog.objects.filter(name__contains='Cheddar').values_list('pk', flat=True)
                       #entries = Entry.objects.filter(blog__in=list(values))
                       paycode = Transcd.objects.filter(transtype='FD').values('transcd','transnm')
                       paylist = []
                       for x in paycode:
                            paylist.append(x['transcd'])

                       emientry = Daybook.objects.filter(date=fdateofentry, locationcode=flocation,drcr='D',transcd__in=list(paylist)).values('locationcode','locationname','transid','appname','personname','transnm','date','loanid','mode').annotate(amount=Coalesce(Sum('amount'),0))
      

                       context = {'loginlocationcode': loginlocationcode,
                                      'loginlocationname': loginlocationname,
                                      'loginrundate': loginrundate,
                                      'currdate':currdate,
                                      'fdateofentry':fdateofentry,
                                      'flocationcode':flocationcode,
                                      'flocationname':flocationname,
                                      'emientry':emientry,
                                    }

                       return render(request, 'admssadmin/admssadmindeletepaymentget.html', context)
                        
                return render(request, 'admssadmin/admssadmindeletepayment.html' , context)



############ DELETE PAYMENT GET ##########
##########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeletepaymentget(request,deletedata_transid):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['H']):
        return HttpResponseRedirect('/login')
    else:



        
            deletedata=Daybook.objects.filter(transid=deletedata_transid)


            ftransid = deletedata[0].transid
            fmode = deletedata[0].mode
            fappbankac = deletedata[0].bankac
            fpersonname =  deletedata[0].personname

            fdateofentry = deletedata[0].date
            fdateofentry = date.strftime(fdateofentry, "%Y-%m-%d")

            ftypeentry = "PAYMENT"


            fnoofrecorddaybok = Daybook.objects.filter(transid=deletedata_transid).count()
            daybookentried = Daybook.objects.filter(transid=deletedata_transid)


            famount = deletedata[0].transid

            context = {'loginlocationcode': loginlocationcode,
                       'loginlocationname': loginlocationname,
                       'loginrundate': loginrundate,
                       'currdate':currdate,
                       'ftransid':ftransid,
                       'ftypeentry':ftypeentry,
                       'fdateofentry':fdateofentry,
                       'fnoofrecorddaybok':fnoofrecorddaybok,
                       'daybookentried':daybookentried,
                       'fpersonname':fpersonname,
                       'famount':famount,
                       'fmode':fmode,
                       'deletedata':deletedata,

                        }


            return render(request, 'admssadmin/admssadmindeletepaymentcommit.html', context)





############ DELETE PAYMENT COMMIT ##########
#############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmindeletepaymentcommit(request):

    loguserid = request.session['loguserid']
    ll=Locationlogin.objects.get(user=loguserid)
      
    loginlocationcode=ll.locationcode
    loginlocationname=ll.locationname
    loginrundate=ll.rundate
    loginstatus = ll.status
    currdate = date.today()


    user = User.objects.get(id=loguserid)
    if user is not None and loginstatus not in(['H']):
        return HttpResponseRedirect('/login')
    else:

            floanid = request.POST.get('loanid')
            ftransid = request.POST.get('transid')

            deletedata=Daybook.objects.filter(transid=ftransid)

            flocationcode = deletedata[0].locationcode
            floanid = deletedata[0].loanid
            ftransid = deletedata[0].transid
            fmode = deletedata[0].mode
            fappbankac = deletedata[0].bankac
            famount = deletedata[0].amount


            fnoofrecorddaybook = Daybook.objects.filter(transid=ftransid).count()

            Daybook.objects.filter(transid=ftransid).delete()

            if fmode == 'CASH':
                allcash = Opclcashbank.objects.filter(locationcode=flocationcode,date=loginrundate)
        
                for all in allcash:
                    all.clcash = all.clcash + famount
                    all.save()

            if fmode == 'BANK':
                allbank = Opclcashbank.objects.get(locationcode=flocationcode,bankac=fappbankac,date=loginrundate)
                allbank.clbank=allbank.clbank + famount
                allbank.save()


            message = "Payment Deleted , Daybook record " + str(fnoofrecorddaybook) +" / "+"Rs."+str(famount)+" / Deleted Succesfully through "+fmode

            messages.success(request, message)
            return HttpResponseRedirect('/admssadmindeletepayment/')




############# USER CREATE ###########
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminusercreate(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'currdate':currdate,
                          }


                if request.method == "POST":

                    fuser = request.POST.get('uname')
                
                    try:
                       alluser = User.objects.get(username=fuser)
                       context = {'loginlocationcode': loginlocationcode,
                                     'loginlocationname': loginlocationname,
                                     'loginrundate': loginrundate,
                                     'currdate':currdate,
                                     'alluser':alluser,
                                     'fuser':fuser,
                                     }
                       message = "User " + fuser + " already exists... "
                       messages.success(request, message)
                       return render(request, 'admssadmin/admssadminusercreateexists.html', context)

                    except  User.DoesNotExist:

                        allperson = Personmaster.objects.all().distinct('personname')
                        context = {'loginlocationcode': loginlocationcode,
                                     'loginlocationname': loginlocationname,
                                     'loginrundate': loginrundate,
                                     'currdate':currdate,
                                     'fuser':fuser,
                                     'allperson':allperson,
                                     }

                        return render(request, 'admssadmin/admssadminusercreateget.html', context)                       
                        
                return render(request, 'admssadmin/admssadminusercreate.html' , context)




############# USER CREATE GET ###########
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminusercreateget(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)

            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            user = User.objects.get(id=loguserid)
            if user is not None and loginstatus not in (['H']):
                  return HttpResponseRedirect('/login')
            else:


                if request.method == "POST":

                    fuser = request.POST.get('uname')
                    fusertype = request.POST.get('usertype')

                
                    try:
                       alluser = User.objects.get(username=fuser)
                       context = {'loginlocationcode': loginlocationcode,
                                     'loginlocationname': loginlocationname,
                                     'loginrundate': loginrundate,
                                     'currdate':currdate,
                                     'alluser':alluser,
                                     'fuser':fuser,
                                     }
                       message = "User " + fuser + " already exists... "
                       messages.success(request, message)
                       return render(request, 'admssadmin/admssadminusercreateexists.html', context)

                    except  User.DoesNotExist:




                        return render(request, 'admssadmin/admssadminusercreateget.html', context)                       
                        




#########################################
##### EMI COLLECTOR DEV EXP REPORT ######
#########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminemicollectorreport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['H']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    ffromdate = loginrundate.strftime("%Y-%m-01")
                    ftodate = loginrundate.strftime("%Y-%m-%d")

                    flocation = Locationlogin.objects.values('locationcode','locationname').filter(~Q(locationcode=loginlocationcode)).distinct().order_by('locationname')         

                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'flocation':flocation,
                            }

                    if request.method == "POST":
                            ffromdate = request.POST.get('fromdate')
                            ftodate=request.POST.get('todate')     
                            flocationcode=request.POST.get('locationcode')
                            fcollcode=request.POST.get('collcode')   

                            location = Locationlogin.objects.get(locationcode=flocationcode,status__in=['B','A'])        
                            flocationcode = location.locationcode
                            flocationname = location.locationname

                            emicoll = Loanmaster.objects.filter(locationcode=flocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')

                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'loginstatus':loginstatus,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'flocationcode':flocationcode,
                                    'flocationname':flocationname,
                                    'emicoll':emicoll,

                                    }
                            return render(request, 'admssadmin/admssadminemicollectorreportget.html' , context)

        
                    return render(request, 'admssadmin/admssadminemicollectorreport.html' , context)



#############################################
##### EMI COLLECTOR DEV EXP REPORT GET ######
#############################################
from django.db.models import FloatField, ExpressionWrapper, F
from django.db import models

@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadminemicollectorreportget(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['H']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate


                    if request.method == "POST":
                            ffromdate = request.POST.get('fromdate')
                            ftodate=request.POST.get('todate')
                            flocation=request.POST.get('locationcode')     

                            fcollcode=request.POST.get('collcode')   

                            emicoll = Loanmaster.objects.filter(locationcode=loginlocationcode,status='A').values('rpersoncode','rpersonname').distinct().order_by('rpersonname')

                            devexp_expr = ExpressionWrapper(
                                Coalesce(
                                    Sum('amount', filter=Q(transcd__in=['3012', '3013']) & Q(loanid__startswith='I')) * 0.1,
                                    0.0,
                                    output_field=FloatField(),
                                )
                                + Coalesce(
                                    Sum('amount', filter=Q(transcd__in=['3012', '3013']) & Q(loanid__startswith='G')) * 0.1 * 0.5,
                                    0.0,
                                    output_field=FloatField(),
                                ),
                                output_field=FloatField(),
                            )

                            #allrecord = Daybook.objects.values('personcode','personname').filter(date__range=(ffromdate,ftodate),locationcode=flocation,transcd__in=['3011','3012','3013','3019']).annotate(totemi=Sum('amount',filter=Q(transcd__in=['3011','3012','3013','3019']))).annotate(totprin=Sum('amount',filter=Q(transcd__in=['3011','3019']))).annotate(totint=Sum('amount',filter=Q(transcd__in=['3012','3013']))).annotate(indiamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='I'))).annotate(groupamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='G'))).order_by('-totemi')
                            allrecord = Daybook.objects.values('personcode','personname').filter(date__range=(ffromdate,ftodate),locationcode=flocation,transcd__in=['3011','3012','3013','3019']).annotate(totemi=Sum('amount',filter=Q(transcd__in=['3011','3012','3013','3019']))).annotate(totprin=Sum('amount',filter=Q(transcd__in=['3011','3019']))).annotate(totint=Sum('amount',filter=Q(transcd__in=['3012','3013']))).annotate(indiamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='I'))).annotate(groupamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='G'))).annotate(devexp=devexp_expr).order_by('-totemi')

                            summ = Daybook.objects.values('locationcode','locationname').filter(date__range=(ffromdate,ftodate),locationcode=flocation,transcd__in=['3011','3012','3013','3019']).annotate(totemi=Sum('amount',filter=Q(transcd__in=['3011','3012','3013','3019']))).annotate(totprin=Sum('amount',filter=Q(transcd__in=['3011','3019']))).annotate(totint=Sum('amount',filter=Q(transcd__in=['3012','3013']))).annotate(indiamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='I'))).annotate(groupamt=Sum('amount',filter=Q(transcd__in=['3012','3013']) & Q(loanid__startswith='G'))).annotate(devexp=devexp_expr)
                            


                            allamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013']).aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))
                            indiamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013'],loanid__startswith='I').aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))
                            groupamt = Daybook.objects.filter(date__range=(ffromdate,ftodate),locationcode=loginlocationcode,personcode=fcollcode,transcd__in=['3011','3012','3019','3013'],loanid__startswith='G').aggregate(totac=Coalesce(Count('loanid',distinct=True),0),totamt=Coalesce(Sum('amount'),0))

                            intamtindi = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, personcode=fcollcode, transcd__in=[
                                                            '3012', '3013'], loanid__startswith='I').aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount'), 0))
                
                            intamtgroup = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, personcode=fcollcode, transcd__in=[
                                                            '3012', '3013'], loanid__startswith='G').aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount'), 0))


                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'loginstatus':loginstatus,
                                    'ffromdate':ffromdate,
                                    'ftodate':ftodate,
                                    'allrecord':allrecord,
                                    'summ':summ,

                                    }
                            return render(request, 'admssadmin/admssadminemicollectorreportshow.html' , context)

        
                    return render(request, 'admssadmin/admssadminemicollectorreport.html' , context)


#################################
##### INSURANCE DUE REPORT ######
#################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssadmininsuranceduereport(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['H']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    fduedate = loginrundate.strftime("%Y-%m-%d")


                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'fduedate':fduedate,
                            }

                    if request.method == "POST":
                            fduedate = request.POST.get('duedate')

                            insduelist = Loanmaster.objects.filter(status='A',applifeinsuruptodate__lte=fduedate)   


                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'loginstatus':loginstatus,
                                    'fduedate':fduedate,
                                    'insduelist':insduelist,
                                    }
                            return render(request, 'admssadmin/admssadmininsuranceduereportshow.html' , context)
        
                    return render(request, 'admssadmin/admssadmininsurancesuereport.html' , context)



#####################################
##### AUTHORISE CENTRE EXPENSE ######
#####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def authcenterexpance(request):
             loguserid = request.session['loguserid']
             ll=Locationlogin.objects.get(user=loguserid)
        
             loginlocationcode=ll.locationcode
             loginlocationname=ll.locationname
             loginrundate=ll.rundate    
             loginstatus = ll.status
             currdate = date.today()

             user = User.objects.get(id=loguserid)
             if user is not None and loginstatus not in(['H']):
                 return HttpResponseRedirect('/login')
             else:

                    ffromdate = ll.rundate
                    ftodate = ll.rundate

                    fduedate = loginrundate.strftime("%Y-%m-%d")

                    lastauthexp = Authcenterexpance.objects.all().order_by('-fromdate')
                    ffromdate = lastauthexp[0].fromdate
                    ftodate = lastauthexp[0].todate

                    lastmonth = ffromdate + relativedelta(months=1)


                    ftodate = lastmonth.replace(day=calendar.monthrange(
                        lastmonth.year, lastmonth.month)[1])
                    ffromdate = lastmonth.strftime("%Y-%m-01")
                    ftodate = ftodate.strftime("%Y-%m-%d")



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
                            ftodate = request.POST.get('todate')

                            ac = Locationlogin.objects.filter(status='A')

                            for x in ac:
                                flocationcode = x.locationcode
                                flocationname = x.locationname

                                eppersonmast = Personmaster.objects.get(locationcode=flocationcode, persontype='ACH')

                                fpersoncode = eppersonmast.personcode
                                fpersonname = eppersonmast.personname


                                fexpensecode = '3376'
                                fexpensename = 'Auth. Center Expense'
                                db = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=flocationcode, transcd__in=['3012'], drcr='C').aggregate(totalac=Coalesce(Count('transcd'), 0), totalamt=Coalesce(Sum('amount'), 0))

                                fexpensetotac = db.get("totalac")
                                fexpensetotamt = db.get("totalamt")
                                fexpensenetamt = int(fexpensetotamt*.8)


                                fspotexpensecode = '3377'
                                fspotexpensename = 'Auth. Center Spot Expense'

                                db = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=flocationcode, transcd__in=['3014'], drcr='C').aggregate(totalac=Coalesce(Count('transcd'), 0), totalamt=Coalesce(Sum('amount'), 0))

                                fspotexpensetotac = db.get("totalac")
                                fspotexpensetotamt = db.get("totalamt")
                                fspotexpensenetamt = int(fspotexpensetotamt) - int(fspotexpensetotamt*2/3)

                                fregfeecode = '3378'
                                fregfeename = 'Auth. Center Reg. Fees'

                                db = Daybook.objects.filter(date__range=(ffromdate, ftodate), locationcode=flocationcode, transcd__in=['3013'], drcr='C').aggregate(totalac=Coalesce(Count('transcd'), 0), totalamt=Coalesce(Sum('amount'), 0))

                                fregfeetotac = db.get("totalac")
                                fregfeetotamt = db.get("totalamt")
                                fregfeenetamt = int(fregfeetotamt)

                                ## check authorise center expense already generated ##
                                ispaid = Authcenterexpance.objects.filter(locationcode=flocationcode, fromdate=ffromdate, todate=ftodate, transcd=fexpensecode)

                                if not ispaid.exists(): 
                                    authcent = Authcenterexpance(locationcode=flocationcode,
                                                                 locationname=flocationname,
                                                         fromdate=ffromdate,
                                                         todate=ftodate,
                                                         totalamount=fexpensetotamt,
                                                         transcd=fexpensecode, transnm=fexpensename,
                                                         personcode=fpersoncode, personname=fpersonname,
                                                         amount=int(fexpensenetamt),
                                                         hqamount = fexpensetotamt - int(fexpensenetamt),
                                                         paid="N",
                                                         hqpaid="N")

                                    authcent.save()

                                ## check authorise center spot expense already generated ##
                                ispaid = Authcenterexpance.objects.filter(locationcode=flocationcode, fromdate=ffromdate, todate=ftodate, transcd=fspotexpensecode)

                                if not ispaid.exists():
                                    authcent = Authcenterexpance(locationcode=flocationcode,
                                                                 locationname=flocationname,
                                                                 fromdate=ffromdate,
                                                                 todate=ftodate,
                                                                 totalamount=fspotexpensetotamt,
                                                                 transcd=fspotexpensecode, transnm=fspotexpensename,
                                                                 personcode=fpersoncode, personname=fpersonname,
                                                                 amount=int(fspotexpensenetamt),
                                                                 hqamount=fspotexpensetotamt - int(fspotexpensenetamt),
                                                                 paid="N",
                                                                 hqpaid="N")

                                    authcent.save()

                                ## check authorise center spot expense already generated ##
                                ispaid = Authcenterexpance.objects.filter(locationcode=flocationcode, fromdate=ffromdate, todate=ftodate, transcd=fregfeecode)

                                if not ispaid.exists():
                                    authcent = Authcenterexpance(locationcode=flocationcode,
                                                                 locationname=flocationname,
                                                                 fromdate=ffromdate,
                                                                 todate=ftodate,
                                                                 totalamount=fregfeetotamt,
                                                                 transcd=fregfeecode, transnm=fregfeename,
                                                                 personcode=fpersoncode, personname=fpersonname,
                                                                 amount=int(fregfeenetamt),
                                                                 hqamount = 0,
                                                                 paid="N",
                                                                 hqpaid="N")

                                    authcent.save()

                            ispaid = Authcenterexpance.objects.filter(fromdate=ffromdate, todate=ftodate)
                            context={'loginlocationcode':loginlocationcode,
                                    'loginlocationname':loginlocationname,
                                    'loginrundate':loginrundate,
                                    'currdate':currdate,
                                    'loginstatus':loginstatus,
                                    'ffromdate': ffromdate,
                                    'ftodate': ftodate,
                                    'ispaid':ispaid,

                                    }
                            return render(request, 'admssadmin/admssadminauthcenterexpanceshow.html', context)
        
                    return render(request, 'admssadmin/admssadminauthcenterexpance.html', context)



##### ADMIN LOGOUT  #####
#########################
@login_required(login_url='login')
def admssadminlogout(request):
    if request.user.is_authenticated:
        del request.session['loguserid']
        django_logout(request)
        return redirect('login')
    else:
        return redirect('login')

