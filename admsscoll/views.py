from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.db.models import Q, F
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from admssapp.models import Locationlogin
from admssapp.models import Loanmaster, Loanscheme, Personmaster
from admssapp.models import Locationlogin, Daybook, Loantrans
from admssapp.models import Opclcashbank
from admssapp.models import Emicolldata
from admssapp.models import Rate

from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import HttpResponseRedirect
from django.contrib import messages

from admssapp.models import Userlogged
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from datetime import date
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout as django_logout

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout as django_logout

from admssapp.utils import render_to_pdf

from admssapp.updateledger import update
from admssapp.updateemi import statices

##################################
########## COLL HOME  ############
##################################
@login_required(login_url='login')
@never_cache
def admsscollhome(request):

        loguserid = request.session['loguserid']

        ll = Locationlogin.objects.get(user_id=loguserid)

        loginlocationcode = ll.locationcode
        loginlocationname = ll.locationname
        loginrundate = ll.rundate
        loginstatus = ll.status

        ip = request.session.get('ip', 0)
        x_forw = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forw:
            ip = x_forw.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        

        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in (['C']):
             return HttpResponseRedirect('/login')
        else:

                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                # fcollday = fappemiduedate.strftime('%w')
                frunday = loginrundate.strftime('%w')
                ###############################################

                ffromdate = ll.rundate
                ftodate = ll.rundate

                ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
                ftodate = ffromdate + timedelta(days=5)

                emidep = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode,master__rpersoncode=rpersoncode).aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount')+Sum('latefee'), 0))

                emiac = emidep.get("totac")
                emiamt = emidep.get("totamt")

 
                allr = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode).select_related('master')
                for all in allr:
                    if all.amount >= all.master.apploanemi:
                        all.flag = "Y"
                    else:
                        all.flag = "N"
                    all.save()

                allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(status='A')).order_by('colldaynum', 'applastemidepdate')

                for all in allnr:
                    if all.appemiduedate > loginrundate:
                        all.delaydays1 = 2
                    else:
                        all.delaydays1 = 1
                    all.save()


                balac = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(
                status='A') & Q(appemiduedate__lte=ftodate)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

                dueac = balac.get("totac")
                dueamt = balac.get("totemi")

                ffromdate = ffromdate.strftime('%d-%m-%Y')
                ftodate = ftodate.strftime('%d-%m-%Y')
                
                ###############################################



                ##############################################
                ##############################################
                start_week = loginrundate - timedelta(loginrundate.weekday())
                end_week = start_week + timedelta(5)

                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")

                frpersoncode = ll.rpersoncode
                newloansumm = Loanmaster.objects.filter(apploandate__range=(ffromdate, ftodate), locationcode=loginlocationcode, rpersoncode=frpersoncode).aggregate(totalloan=Coalesce(Count('loanid'), 0),totalloanamt=Coalesce(Sum('apploanamt'), 0),totalloanemi=Coalesce(Sum('apploanemi'), 0))
                settledloansumm = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate, ftodate), locationcode=loginlocationcode, rpersoncode=frpersoncode).aggregate(totalloan=Coalesce(Count('loanid'), 0),totalloanamt=Coalesce(Sum('apploanamt'), 0),totalloanemi=Coalesce(Sum('apploanemi'), 0))

                newac = newloansumm.get("totalloan")
                newemi = newloansumm.get("totalloanemi")

                settledac = settledloansumm.get("totalloan")
                settledemi = settledloansumm.get("totalloanemi")

                ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").strftime("%d-%m-%Y")
                ftodate = datetime.strptime(ftodate, "%Y-%m-%d").strftime("%d-%m-%Y")



                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'ip':ip,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'emiac': emiac,
                        'emiamt': emiamt,
                        'dueac': dueac,
                        'dueamt': dueamt,
                        'newac': newac,
                        'newemi': newemi,
                        'settledac': settledac,
                        'settledemi': settledemi
                        }

                return render(request, 'admsscoll/home.html', context)


##################################
########## EMI DEPOSIT ###########
##################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemideposit(request):

     # if request.user.is_authenticated:

         loguserid = request.session['loguserid']

         ll = Locationlogin.objects.get(user_id=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in (['C']):
              return HttpResponseRedirect('/login')
         else:

                
                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                nname = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('appname')
                nnameday = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('colldaynum', 'appname')
                success = False
                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'nname': nname,
                        'nnameday': nnameday,
                        'success': False,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        }

                if request.method == "POST":

                        fapploanid = request.POST.get('name')

                        loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)
                        loanledsumm1 = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').aggregate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0))

                        fapploanid = loanmast.loanid
                        fappname = loanmast.appname
                        fapploanemi = loanmast.apploanemi
                        fapplastemidepdate = loanmast.applastemidepdate
                        fapploandate = loanmast.apploandate
                        fappemiduedate = loanmast.appemiduedate
                        fapptotalrecamt = loanmast.apptotalrecamt
                        fapploanamt = loanmast.apploanamt
                        fappoccupation = loanmast.appoccupation
                        fappshoplocation = loanmast.appshoplocation
                        fadminpersonname = loanmast.adminpersonname

                        flocationcode = loginlocationcode
                        flocationname = loginlocationname
                        flastemiday = ''
                        #flastemiday = fapplastemidepdate.strftime('%A')
                        femiday = loanmast.colldaychar

                        flatefees = loanledsumm1.get("totlatefee")

                        loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')

                        fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)

                        fcaldays, fint, fexcessint, totaldays,ftenuoverdue, ftotalemidue, fcurremidue, fcurrdueamt, fcurremidone, fcurremibal, fcurroverdue, ftenuoverdue = statices(fapploanid, loginlocationcode, loginrundate)

                        foverdueamt =  int((loanmast.apploanamt/1000) * totaldelaydays)
                        ftotaldueamt = fcurrdueamt + foverdueamt - flatefees  

                        latefee = int((loanmast.apploanamt/1000) * fdelaydays)

                        allbank = Opclcashbank.objects.filter(locationcode=loginlocationcode, date=loginrundate)

                        context = {'loginlocationcode': loginlocationcode,
                                'loginlocationname': loginlocationname,
                                'loginrundate': loginrundate,
                                'rpersoncode': rpersoncode,
                                'rpersonname': rpersonname,
                                'fapploanid': fapploanid,
                                'fappname': fappname,
                                'fapploanemi': fapploanemi,
                                'fapplastemidepdate': fapplastemidepdate,
                                'fappemiduedate': fappemiduedate,
                                'fapptotalrecamt': fapptotalrecamt,
                                'allbank': allbank,
                                'fdelaydays': fdelaydays,
                                'latefee': latefee,
                                'fappoccupation': fappoccupation,
                                'fappshoplocation': fappshoplocation,
                                'fadminpersonname': fadminpersonname,
                                'femiday':femiday,
                                'fapploanamt': fapploanamt,
                                'fcurremidue':fcurremidue,
                                'fcurremidone':fcurremidone,
                                'fcurroverdue':fcurroverdue,
                                 }

                        return render(request, 'admsscoll/collemiprocess.html', context)

                else:
                    return render(request, 'admsscoll/collemideposit.html', context)


#################### ##############
############ EMI COMMIT############
###################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemicommit(request):

    # if request.user.is_authenticated:
         loguserid = request.session['loguserid']

         ll = Locationlogin.objects.get(user_id=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status

         user = User.objects.get(id=loguserid)

         if user is not None and loginstatus not in (['C']):
              return HttpResponseRedirect('/login')
         else:

                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                if request.method == "POST":
                    fapploanid = request.POST.get('loanidname')
                    fcashrec = 0
                    flatefee = 0
                    femidelaydays = 0
                    femidelayamt = 0



                    if len(request.POST.get('cashrec')) > 0:
                        fcashrec = int(request.POST.get('cashrec'))

                    if len(request.POST.get('latefee')) > 0:
                        flatefee = int(request.POST.get('latefee'))

                    if len(request.POST.get('emidelaydays')) > 0:
                        femidelaydays = int(request.POST.get('emidelaydays'))

                    if len(request.POST.get('emidelayamt')) > 0:
                        femidelayamt = int(request.POST.get('emidelayamt'))





                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode, loanid=fapploanid)

                    loanledtmp = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('-date')

                    if loanledtmp:
                        fdelaydays = (loginrundate - loanledtmp[0].date).days
                    else:
                        fdelaydays = 0
                        

                    fmasterid = loanmast.id
                    fapploanid = loanmast.loanid
                    fappname = loanmast.appname
                    fapploanemi = loanmast.apploanemi
                    fapploanemiprin = loanmast.apploanemiprin
                    fapploanemiint = loanmast.apploanemiint
                    fappemiduedate = loanmast.appemiduedate
                    fapplastemidepdate = loanmast.applastemidepdate
                    fapploanamt = loanmast.apploanamt

                    fpersoncode = loanmast.rpersoncode
                    fpersonname = loanmast.rpersonname

                    flocationcode = loginlocationcode
                    flocationname = loginlocationname

                    if fcashrec > 0:
                        emicoll = Emicolldata(locationcode=loginlocationcode,
                                locationname=loginlocationname,
                                loanid=fapploanid, appname=fappname,
                                apploanemi=fapploanemi,
                                rundate=loginrundate, date=datetime.now(),
                                lastemidepdate=fapplastemidepdate,
                                emiduedate=fappemiduedate,
                                rpersoncode=fpersoncode, rpersonname=fpersonname,
                                #delaydays=fdelaydays,
                                status='N', amount=fcashrec,
                                latefee=flatefee,
                                delaydays=femidelaydays,
                                delayamount=femidelayamt,
                                user_id=loguserid, master_id=fmasterid)

                        emicoll.save()

                    success = True

                    nname = Loanmaster.objects.filter(
                        locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('appname')
                    nloanid = Loanmaster.objects.filter(
                        locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('loanid')

                    message = "EMI of "+fappname+" / "+fapploanid+" / "+"Rs." + \
                        str(fcashrec)+" / Received Succesfully through Cash."

                    messages.success(request, message)
                    return HttpResponseRedirect('/collemideposit/')


########################################
########## GROUP EMI DEPOSIT ###########
########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collgroupemideposit(request):

         loguserid = request.session['loguserid']
         ll = Locationlogin.objects.get(user=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)

         if user is not None and loginstatus not in (['C']):
               return HttpResponseRedirect('/login')
         else:

             rpersoncode = ll.rpersoncode
             rpersonname = ll.rpersonname

             ngroupname = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, groupemicoll='N', status='A', groupleader='Y',
                                                    appemiduedate__lte=loginrundate+timedelta(1)).values('groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')
             ngroupid = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, groupemicoll='N', status='A', groupleader='Y').values(
                 'groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')

             context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'currdate': currdate,
                        'ngroupname': ngroupname,
                        'ngroupid': ngroupid,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'success': False,
                          }

             if request.method == "POST" and 'show' in request.POST:
                        fgroupid = request.POST.get('groupidname')

                        groupleager = Loanmaster.objects.get(
                            locationcode=loginlocationcode, groupid=fgroupid, groupleader='Y')

                        fgroupid = groupleager.groupid
                        fgroupleadername = groupleager.groupleadername
                        fgrouplocation = groupleager.appshoplocation
                        floanemi = groupleager.apploanemi
                        fgroupemi = groupleager.grouploanemi

                        context = {'loginlocationcode': loginlocationcode,
                                'loginlocationname': loginlocationname,
                                'loginrundate': loginrundate,
                                'currdate': currdate,
                                'fgroupid': fgroupid,
                                'fgroupleadername': fgroupleadername,
                                'fgrouplocation': fgrouplocation,
                                'fgroupemi': fgroupemi,
                                'floanemi': floanemi,
                                 }

                        return render(request, 'admsscoll/collgroupemidepositget.html', context)
             else:

                 return render(request, 'admsscoll/collgroupemideposit.html', context)


############################################
########## GROUP EMI DEPOSIT GET ###########
############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collgroupemidepositget(request):

            loguserid = request.session['loguserid']
            ll = Locationlogin.objects.get(user=loguserid)
            loginlocationcode = ll.locationcode
            loginlocationname = ll.locationname
            loginrundate = ll.rundate
            loginstatus = ll.status
            currdate = date.today()

            rpersoncode = ll.rpersoncode
            rpersonname = ll.rpersonname

            if request.method == "POST" and 'show' in request.POST:

                        fgroupid = request.POST.get('groupidname')
                        floanemi = request.POST.get('emiamount')

                        ngroupname = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, status='A', groupleader='Y').order_by('id')
                        epgroupleager = Loanmaster.objects.get(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A', groupid=fgroupid, groupleader='Y')

                        allgroupac = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, status='A').order_by('id')

                        for all in allgroupac:

                            all.grouploanemi = floanemi
                            all.save()

                        allgroupac = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, status='A').order_by('id')

                        summ = Loanmaster.objects.filter(locationcode=loginlocationcode, groupid=fgroupid, status='A').aggregate(totac=Coalesce(
                            Count('loanid'), 0), totemi=Coalesce(Sum('apploanemi'), 0), totamt=Coalesce(Sum('grouploanemi'), 0))

                        tac = summ.get("totac")
                        temi = summ.get("totemi")
                        tamt = summ.get("totamt")

                        if tamt == 0:
                            tamt = temi

                        fgroupid = epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation

                        context = {'loginlocationcode': loginlocationcode,
                                 'loginlocationname': loginlocationname,
                                 'loginrundate': loginrundate,
                                 'currdate': currdate,
                                 'ngroupname': ngroupname,
                                 'allgroupac': allgroupac,
                                 'tac': tac,
                                 'temi': temi,
                                 'tamt': tamt,
                                 'rpersoncode': rpersoncode,
                                 'rpersonname': rpersonname,
                                 'success': False,
                                   }
                        return render(request, 'admsscoll/collgroupemidepositlist.html', context)


###############################################
########## GROUP EMI DEPOSIT COMMIT ###########
###############################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collgroupemidepositcommit(request):

         loguserid = request.session['loguserid']
         ll = Locationlogin.objects.get(user=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status
         currdate = date.today()

         user = User.objects.get(id=loguserid)

         if user is not None and loginstatus not in (['C']):
               return HttpResponseRedirect('/login')
         else:

             rpersoncode = ll.rpersoncode
             rpersonname = ll.rpersonname

             ngroupname = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, groupemicoll='N', status='A', groupleader='Y',
                                                    appemiduedate__lte=loginrundate+timedelta(1)).values('groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')
             ngroupid = Loanmaster.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, groupemicoll='N', status='A', groupleader='Y').values(
                 'groupid', 'groupleadername', 'appshoplocation').distinct().order_by('groupid', 'apploandate')

             context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'currdate': currdate,
                        'ngroupname': ngroupname,
                        'ngroupid': ngroupid,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'success': False,
                          }

             if request.method == "POST" and 'show' in request.POST:

                        fgroupid = request.POST.get('groupidname')

                        epgrouploan = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid).order_by('id')
                        epgroupleager = Loanmaster.objects.get(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, groupleader='Y')

                        fgroupid = epgroupleager.groupid
                        fgroupleadername = epgroupleager.groupleadername
                        fgrouplocation = epgroupleager.appshoplocation

                        for all in epgrouploan:
                            if all.apploanemi > all.grouploanemi:
                                famount = all.apploanemi
                            else:
                                famount = all.grouploanemi

                            delta = loginrundate-all.appemiduedate
                            delaydays = (delta.days)
                            latefee = int((delta.days)*(all.apploanamt*.001))
                            if latefee <= 0:
                                latefee = 0

                            emicoll = Emicolldata(locationcode=all.locationcode,
                                                  locationname=all.locationname,
                                                  loanid=all.loanid,
                                                  appname=all.appname,
                                                  rundate=loginrundate,
                                                  date=datetime.now(),
                                                  lastemidepdate=all.applastemidepdate,
                                                  emiduedate=all.appemiduedate,
                                                  rpersoncode=rpersoncode,
                                                  rpersonname=rpersonname,
                                                  delaydays=delaydays,
                                                  status='N',
                                                  groupid=fgroupid,
                                                  amount=famount,
                                                  user_id=loguserid,
                                                  master_id=all.id)

                            emicoll.save()
                            all.groupemicoll = 'Y'
                            all.save()

                        epgrouploan = Emicolldata.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, status='N').order_by('id')

                        summ = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, groupid=fgroupid, status='N').aggregate(totac=Coalesce(
                                   Count('loanid'), 0), totamt=Coalesce(Sum('amount'), 0))

                        tac = summ.get("totac")
                        tamt = summ.get("totamt")

                        nname = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('appname')
                        nloanid = Loanmaster.objects.filter(
                            locationcode=loginlocationcode, rpersoncode=rpersoncode, status='A').order_by('loanid')

                        message = "Group EMI of "+fgroupleadername+" / "+fgrouplocation+" / " + \
                            "Rs."+str(tamt) + \
                            " / Received Succesfully through Cash."

                        messages.success(request, message)
                        return HttpResponseRedirect('/collgroupemideposit/')
             else:

                 return render(request, 'admsscoll/collgroupemideposit.html', context)


###########################################
########## EMI COLLETION REPORT ###########
###########################################
@login_required(login_url='login')
@csrf_exempt
def collemireport(request):

         loguserid = request.session['loguserid']

         ll = Locationlogin.objects.get(user_id=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in (['C']):
            return HttpResponseRedirect('/login')
         else:

                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        }

                allcolldata = Emicolldata.objects.filter(
                    locationcode=loginlocationcode, rpersoncode=rpersoncode, status='N').order_by('rpersoncode')

                collsumm = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, status='N').values(
                    'rpersoncode', 'rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'), 0)).order_by('rpersoncode')
                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, status='N').values(
                    'locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'), 0))

                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'allcolldata': allcolldata,
                        'collsumm': collsumm,
                        }

                return render(request, 'admsscoll/collemireport.html', context)


######################################################
########## EMI COLLECTION PROCESSED REPORT ###########
######################################################
@login_required(login_url='login')
@csrf_exempt
def collemireportall(request):

         loguserid = request.session['loguserid']

         ll = Locationlogin.objects.get(user_id=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in (['C']):
              return HttpResponseRedirect('/login')
         else:

                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        }

                allcolldata = Emicolldata.objects.filter(
                    locationcode=loginlocationcode, rpersoncode=rpersoncode, rundate=loginrundate, status__in=['N', 'Y']).order_by('rpersoncode')

                collsumm_up = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, rundate=loginrundate, status='N').values(
                    'rpersoncode', 'rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'), 0)).order_by('rpersoncode')
                collsumm_pp = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, rundate=loginrundate, status='Y').values(
                    'rpersoncode', 'rpersonname').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'), 0)).order_by('rpersoncode')

                collsummall = Emicolldata.objects.filter(locationcode=loginlocationcode, rpersoncode=rpersoncode, status='N').values(
                    'locationcode').annotate(totac=Count('loanid')).annotate(totamt=Coalesce(Sum('amount'), 0))

                context = {'loginlocationcode': loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'allcolldata': allcolldata,
                        'collsumm_up': collsumm_up,
                        'collsumm_pp': collsumm_pp,
                        }

                return render(request, 'admsscoll/collemireportall.html', context)


#################################
#### COLL EMI DEPOSIT REPORT ####
#################################


@login_required(login_url='login')
@csrf_exempt
@never_cache
def collemipendingreport(request):

        loguserid = request.session['loguserid']
        ll = Locationlogin.objects.get(user=loguserid)

        loginlocationcode = ll.locationcode
        loginlocationname = ll.locationname
        loginrundate = ll.rundate
        loginstatus = ll.status
        currdate = date.today()

        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in (['C']):
            return HttpResponseRedirect('/login')
        else:

            rpersoncode = ll.rpersoncode
            rpersonname = ll.rpersonname

            ffromdate = ll.rundate
            ftodate = ll.rundate

            ffromdate = loginrundate - timedelta(days=loginrundate.weekday())
            ftodate = ffromdate + timedelta(days=5)

            dueac = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(status='A') & (Q(appemiduedate__lte=ftodate) | Q(applastemidepdate__gte=ffromdate))).values('locationcode', 'locationname').aggregate(totalac=Coalesce(Count('loanid'), 0), totalloan=Coalesce(Sum('apploanamt'), 0), totalemi=Coalesce(Sum('apploanemi'), 0))
            totalac = Loanmaster.objects.filter(Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(status='A')).values('locationcode', 'locationname').aggregate(totalac=Coalesce(Count('loanid'), 0), totalloan=Coalesce(Sum('apploanamt'), 0), totalemi=Coalesce(Sum('apploanemi'), 0))

            dac = dueac.get("totalac")
            damt = dueac.get("totalloan")
            demi = dueac.get("totalemi")

            tac = totalac.get("totalac")
            tamt = totalac.get("totalloan")
            temi = totalac.get("totalemi")

            settletotal = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate, ftodate), locationcode=loginlocationcode, status='C', rpersoncode=rpersoncode).aggregate(
                totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

            sac = settletotal.get("totac")
            samt = settletotal.get("totloan")
            semi = settletotal.get("totemi")

            #emidep = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode).select_related('master').filter(rpersoncode=rpersoncode).aggregate(
            #    totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount')+Sum('latefee'), 0))

            emidep = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode,master__rpersoncode=rpersoncode).aggregate(totac=Coalesce(Count('loanid', distinct=True), 0), totamt=Coalesce(Sum('amount')+Sum('latefee'), 0))

            emiac = emidep.get("totac")
            emiamt = emidep.get("totamt")

 
            allr = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode).select_related('master')
            for all in allr:
                if all.amount >= all.master.apploanemi:
                    all.flag = "Y"
                else:
                    all.flag = "N"
                all.save()

            allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(status='A')).order_by('colldaynum', 'applastemidepdate')

            for all in allnr:
                if all.appemiduedate > loginrundate:
                    all.delaydays1 = 2
                else:
                    all.delaydays1 = 1
                all.save()

            allr = Loantrans.objects.filter(date__range=(ffromdate, ftodate), locationcode=loginlocationcode, master__rpersoncode=rpersoncode).order_by('date', 'id')
            allnr = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(status='A') & Q(appemiduedate__lte=ftodate)).order_by('colldaynum', 'applastemidepdate')

            balac = Loanmaster.objects.filter((Q(applastemidepdate__lt=(ffromdate)) | Q(applastemidepdate__isnull=True)) & Q(locationcode=loginlocationcode) & Q(rpersoncode=rpersoncode) & Q(
                status='A') & Q(appemiduedate__lte=ftodate)).aggregate(totac=Coalesce(Count('loanid'), 0), totloan=Coalesce(Sum('apploanamt'), 0), totemi=Coalesce(Sum('apploanemi'), 0))

            bac = balac.get("totac")
            bamt = balac.get("totloan")
            bemi = balac.get("totemi")

            ffromdate = ffromdate.strftime('%d-%m-%Y')
            ftodate = ftodate.strftime('%d-%m-%Y')
           
            context = {'loginlocationcode': loginlocationcode,
                       'loginlocationname': loginlocationname,
                       'loginrundate': loginrundate,
                       'loginstatus': loginstatus,
                       'currdate': currdate,
                       'rpersoncode': rpersoncode,
                       'rpersonname': rpersonname,
                       'emiac': emiac,
                       'emiamt': emiamt,
                       'ffromdate': ffromdate,
                       'ftodate': ftodate,
                       'tac': tac,
                       'tamt': tamt,
                       'temi': temi,
                       'dac': dac,
                       'damt': damt,
                       'demi': demi,
                       'sac': sac,
                       'samt': samt,
                       'semi': semi,
                       'bac': bac,
                       'bemi': bemi,
                       'allr': allr,
                       'allnr': allnr,
                       'dueac': dueac,
                       'totalac': totalac,
                            }

            return render(request, 'admsscoll/collemidepositreport.html', context)


######################
#### LOAN LEDGER  ####
######################
@login_required(login_url='login')
@csrf_exempt
def collloanledger(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate
         loginstatus=ll.status

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['C']):
              return HttpResponseRedirect('/login')
         else:

                rpersoncode=ll.rpersoncode
                rpersonname=ll.rpersonname
        
                nname = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=rpersoncode,status="A").order_by('appname')
                nloanid = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=rpersoncode,status="A").order_by('loanid')

                context={'loginlocationcode':loginlocationcode,
                        'loginlocationname':loginlocationname,
                        'loginrundate':loginrundate,
                        'rpersoncod':rpersoncode,
                        'rpersonname':rpersonname,
                        'nname':nname,
                        'nloanid':nloanid,

                        }

                
            
                if request.method == "POST" and 'show' in request.POST:

                    fapploanid = request.POST.get('loanidname')
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).order_by('date', 'id')
                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)

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
                    fmobileno = loanmast.appmobileno
                    fapptotalrecamt = loanmast.apptotalrecamt

                    fcollday = fappemiduedate.strftime('%A')
                    fadminpersonname = loanmast.adminpersonname

                    ftenrexpireon = fapploandate + timedelta(days=fapploantenr)                    

                    fappemiduedate, fdelaydays, fdepamt, fcaldepamt, fcaldepdate, totaldelaydays = update(fapploanid, loginlocationcode, loginrundate)
                    
                    loanled = Loantrans.objects.filter(locationcode=loginlocationcode,loanid=fapploanid).order_by('date','id')
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))
                    



                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'rpersoncod':rpersoncode,
                            'rpersonname':rpersonname,
                            'loanled':loanled,
                            'loanledsumm':loanledsumm,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
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
                            'fapptotalrecamt': fapptotalrecamt,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fcollday':fcollday,
                            'fmobileno': fmobileno,
                            'fadminpersonname':fadminpersonname,
                            'ftenrexpireon':ftenrexpireon,
                                }
                             
                    return render(request, 'admsscoll/collloanledgershow.html' , context)

                elif request.method == "POST" and 'pdf' in request.POST:

                    fapploanid = request.POST.get('loanidname')

                    loanmast = Loanmaster.objects.get(locationcode=loginlocationcode,loanid=fapploanid)

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

                    fapptotalrecamt = loanmast.apptotalrecamt

                    fcollday = fappemiduedate.strftime('%A')

                    
            
                    fstatus = loanmast.status
                    if fstatus == "A":
                        fapploanstatus="Active"
                    else:
                        fapploanstatus="Closed"
                
                    fapppresentadd = loanmast.apppresentadd
                    fapppresentaddcity = loanmast.apppresentaddcity
                    fappmobileno = loanmast.appmobileno
                    fcoappname = loanmast.coappname

                    fappemiduedate, fdelaydays = update(
                        fapploanid, loginlocationcode, loginrundate)
                    
                    loanled = Loantrans.objects.filter(
                        locationcode=loginlocationcode, loanid=fapploanid)
                    loanledsumm = Loantrans.objects.filter(locationcode=loginlocationcode, loanid=fapploanid).values('loanid').annotate(totalac=Coalesce(Count('id'),0),totdep=Coalesce(Sum('amount'),0),totlatefee=Coalesce(Sum('latefee'),0),totaldelaydays=Coalesce(Sum('delaydays'),0))                
                    
                    context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loanled':loanled,
                            'loanledsumm': loanledsumm,
                            'fappname':fappname,
                            'fapploanid':fapploanid,
                            'fapploanamt':fapploanamt,
                            'fapploandate':fapploandate,
                            'fapploantenr':fapploantenr,
                            'fapploanemi':fapploanemi,
                            'fapploandays':fapploandays, 
                            'fappshoplocation':fappshoplocation,
                            'fappoccupation':fappoccupation,
                            'fapptotalrecamt': fapptotalrecamt,
                            'fappshopadd':fappshopadd,
                            'fappemifreq':fappemifreq,
                            'fapploanint':fapploanint,
                            'fapploanstatus':fapploanstatus,
                            'fapppresentadd':fapppresentadd,
                            'fappmobileno':fappmobileno,
                            'fcoappname':fcoappname,
                            'fapppresentaddcity':fapppresentaddcity,
                            'fapplastemidepdate':fapplastemidepdate,
                            'fappemiduedate':fappemiduedate,
                            'fcollday':fcollday,
                                }
                
                    pdf = render_to_pdf('admsscoll/collloanledgerpdf.html', context)
                    return HttpResponse(pdf, content_type='application/pdf')
                
            
                else:
                    return render(request, 'admsscoll/collloanledger.html' , context)





####################################
########## ALL LOAN LIST ###########
####################################
@login_required(login_url='login')
@csrf_exempt
def collloanlist(request):

         loguserid = request.session['loguserid']

         ll = Locationlogin.objects.get(user_id=loguserid)

         loginlocationcode = ll.locationcode
         loginlocationname = ll.locationname
         loginrundate = ll.rundate
         loginstatus = ll.status

         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in (['C']):
             return HttpResponseRedirect('/login')
         else:

                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname

                start_week = loginrundate - timedelta(loginrundate.weekday())
                end_week = start_week + timedelta(5)

                allr = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A", rpersoncode=rpersoncode).order_by('colldaynum')
                loanmastsumm = Loanmaster.objects.filter(locationcode=loginlocationcode, status="A", rpersoncode=rpersoncode).values('rpersoncode').annotate(totac=Coalesce(Count('id'),0),totemi=Coalesce(Sum('apploanemi'),0),totamt=Coalesce(Sum('apploanamt'),0))

                context ={'loginlocationcode':loginlocationcode,
                        'loginlocationname': loginlocationname,
                        'loginrundate': loginrundate,
                        'rpersoncode': rpersoncode,
                        'rpersonname': rpersonname,
                        'allr': allr,
                        'loanmastsumm':loanmastsumm,
                         }

                return render(request, 'admsscoll/collloanlist.html', context)




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
             if user is not None and loginstatus not in (['C']):
                 return HttpResponseRedirect('/login')
             else:


                    rpersoncode = ll.rpersoncode
                    rpersonname = ll.rpersonname
                
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
                            
           
                            allemilist = Loanmaster.objects.filter(locationcode=loginlocationcode,rpersoncode=frpersoncode,status='A').order_by('colldaynum')
                    
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


####################################
####  COLLECTOR NEW LOAN REPORT ####
####################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collnewloanreport(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate    
         loginstatus = ll.status
         currdate = date.today()



         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['C']):
                return HttpResponseRedirect('/login')
         else:


                # ffromdate = ll.rundate
                # ftodate = ll.rundate
                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")
        
                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname
                
                frpersoncode = rpersoncode

                newloansumm = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode,rpersoncode=frpersoncode).values('locationcode','rpersoncode').annotate(total=Coalesce(Count('loanid'),0)).annotate(totalloanamt=Coalesce(Sum('apploanamt'),0)).annotate(totalloanemi=Coalesce(Sum('apploanemi'),0))
                allnewloan = Loanmaster.objects.filter(apploandate__range=(ffromdate,ftodate),locationcode=loginlocationcode,rpersoncode=frpersoncode).order_by('colldaynum','id')

                ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").strftime("%d-%m-%Y")
                ftodate = datetime.strptime(ftodate, "%Y-%m-%d").strftime("%d-%m-%Y")
            
                context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'rpersoncode':rpersoncode,
                            'rpersonname':rpersonname,
                            'newloansumm':newloansumm,
                            'allnewloan':allnewloan,

                            }
            
                return render(request, 'admsscoll/collnewloanreport.html' , context)

###########################################
####  COLLECTOR LOAN SETTLEMENT REPORT ####
###########################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def collsettledloanreport(request):

         loguserid = request.session['loguserid']
         ll=Locationlogin.objects.get(user=loguserid)
        
         loginlocationcode=ll.locationcode
         loginlocationname=ll.locationname
         loginrundate=ll.rundate    
         loginstatus = ll.status
         currdate = date.today()



         user = User.objects.get(id=loguserid)
         if user is not None and loginstatus not in(['C']):
                return HttpResponseRedirect('/login')
         else:


                # ffromdate = ll.rundate
                # ftodate = ll.rundate
                ffromdate = loginrundate.strftime("%Y-%m-01")
                ftodate = loginrundate.strftime("%Y-%m-%d")
        
                rpersoncode = ll.rpersoncode
                rpersonname = ll.rpersonname
                
                frpersoncode = rpersoncode

                settledloansumm = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,rpersoncode=frpersoncode).values('locationcode','rpersoncode').annotate(total=Coalesce(Count('loanid'),0)).annotate(totalloanamt=Coalesce(Sum('apploanamt'),0)).annotate(totalloanemi=Coalesce(Sum('apploanemi'),0))
                allsettledloan = Loanmaster.objects.filter(apploansettlementdate__range=(ffromdate,ftodate),locationcode=loginlocationcode,rpersoncode=frpersoncode).order_by('apploansettlementdate')

                ffromdate = datetime.strptime(ffromdate, "%Y-%m-%d").strftime("%d-%m-%Y")
                ftodate = datetime.strptime(ftodate, "%Y-%m-%d").strftime("%d-%m-%Y")
            
                context={'loginlocationcode':loginlocationcode,
                            'loginlocationname':loginlocationname,
                            'loginrundate':loginrundate,
                            'loginstatus':loginstatus,
                            'currdate':currdate,
                            'ffromdate':ffromdate,
                            'ftodate':ftodate,
                            'rpersoncode':rpersoncode,
                            'rpersonname':rpersonname,
                            'settledloansumm':settledloansumm,
                            'allsettledloan':allsettledloan,
                              }
            
                return render(request, 'admsscoll/collsettledloanreport.html' , context)



##### ADMIN LOGOUT  ##### 
@login_required(login_url='login')
def admsscolllogout(request):
    if request.user.is_authenticated:
        del request.session['loguserid']
        django_logout(request)
        return redirect('admsscollhome')
    else:
        return redirect('admsscollhome')

