from django.shortcuts import render,redirect,HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.contrib import auth

from django.db.models import Q

from django.contrib.auth.models import User
from admssapp.models import Locationlogin
from admssapp.models import Loanmaster,Loanscheme,Personmaster
from admssapp.models import Locationlogin,Daybook,Loantrans
from admssapp.models import Opclcashbank
from admssapp.models import Emicolldata
from admssapp.models import Rate
from admssapp.models import Crifdata
from admssapp.models import Licdata
from admssapp.models import Auditloanmaster20202021, Auditloanrecov20192020, Auditloanmaster20212022
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
 



########## INSURANCE HOME  ###########
######################################
@login_required(login_url='login')
@csrf_exempt
@never_cache
def admssinsurancehome(request):
        
        loguserid = request.session['loguserid']

        ll=Locationlogin.objects.get(user_id=loguserid)
      
        loginlocationcode=ll.locationcode
        loginlocationname=ll.locationname
        loginrundate=ll.rundate
        loginstatus = ll.status
        currdate = date.today()
        loginusercode = ll.rpersoncode
        loginusername = ll.rpersonname

        user = User.objects.get(id=loguserid)
        if user is not None and loginstatus not in (['I']):
            return HttpResponseRedirect('/login')
        else:




                       context={'loginlocationcode' : loginlocationcode,
                               'loginlocationname' : loginlocationname,
                               'loginusercode': loginusercode,
                               'loginusername': loginusername,
                               'loginrundate' : loginrundate,
                               'loginstatus' : loginstatus,
                               'currdate':currdate,

                                }
 
                       return render(request, 'admssinsurance/home.html', context )



##### ADMIN LOGOUT  #####
#########################
@login_required(login_url='login')
def admssinsurancelogout(request):
    if request.user.is_authenticated:
        del request.session['loguserid']
        django_logout(request)
        return redirect('login')
    else:
        return redirect('login')
