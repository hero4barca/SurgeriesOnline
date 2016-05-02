from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from surgeriesOnline.models import *
from surgeriesOnline.forms import *
from surgeriesOnline.view_dir.views import success
from decimal import *
import datetime, re
from surgeriesOnline import tasks
from django.core.mail import send_mail

def user_is_speciFaciUser( user):
    try:
        specFaciUser = SpecializedFacility.objects.get(user=user)
    except SpecializedFacility.DoesNotExist:
        return False
    return user.is_authenticated()


#close referral
def close_referral(request, referralId):
    """
    closes referral - marks as completed
    :param request: http request
    :param referralId: referral Id
    :return: http response
    """

    theReferral = Referral.objects.get(pk=referralId)
    theReferral.status = True
    theReferral.save()

    return hospital_referrals(request)


def scheduled_referrals(request):
    """
    displays scheduled referrals
    :param request: http request
    :return: http response
    """

    try:

        referrals = Referral.objects.filter(specializedFacility__user= request.user,
                                            status= False,
                                            fixed=True)
    except Referral.DoesNotExist:
        referrals = None

    return render(request, 'hospital/scheduled_referrals.html', {'referrals': referrals,
                                                                 'today': datetime.datetime.now() })

@user_passes_test(user_is_speciFaciUser,login_url="/accounts/login/")
def hospital_referrals(request):
    """
    displays referrals
    :param request: http request
    :return: http response
    """
    try:

        referrals = Referral.objects.filter(specializedFacility__user= request.user,
                                            status= False,
                                            fixed=False)
    except Referral.DoesNotExist:
        referrals = None

    return render(request, 'hospital/hospital_referrals.html', {'referral': referrals,
                                                        'today': datetime.datetime.now()
                                                                })

def referral_details(request, referralId):
    """
    displays the details of a referral
    :param request: http request
    :param referralId: referral Id
    :return: http response
    """

    theReferral = Referral.objects.get(pk = referralId)
    theAppointment = theReferral.doctorAppointment
    thePatient = theAppointment.doctorBooking.patient

    return render(request, 'hospital/referral_details.html', {'referral':theReferral,
                                                    'patient': thePatient,
                                                    'appointment': theAppointment})

def fix_referral(request, referralId, error=None):
    """
    displays form to fix referral appointment
    :param request: http request
    :param referralId: referral Id
    :param error: form errors
    :return: http response
    """

    if 'referralId'not in request.session:
        request.session['referralId'] = referralId

    return render(request, 'hospital/fix_referral_appointment.html', {'errors':error
                                                                      })
#
def save_ref_appointment(request ):
    """
    save proposed appointment for referral
    :param request: http request
    :return: http response
    """

    referralId =   request.session['referralId']
    thereferral = Referral.objects.get(pk=referralId)
    errors = []

    if request.method == 'POST':
        if not request.POST.get('fixedDate',''):
            errors.append('please choose date')
        else:
            fixedDate = request.POST.get('fixedDate','')

        if not request.POST.get('fixedTime',''):
            errors.append('please choose time')
        else:
            fixedTime = request.POST.get('fixedTime','')

        if len(errors) < 1:
            dateSplit = re.split('/', fixedDate)
            timesplit = re.split(',', fixedTime)

            if len(dateSplit) ==3:
                try:
                    theDate  = datetime.date(year= int(dateSplit[2]), month= int(dateSplit[1]), day= int(dateSplit[0]))
                except:
                    errors.append('invalid  date input')
            else:
                errors.append('invalid  date input')

            try:
                if len(timesplit)==1:
                    theTime = datetime.time(hour=int(timesplit[0]))
                else :
                    theTime = datetime.time(hour=int(timesplit[0]), minute=int(timesplit[1]))
            except:
                errors.append('invalid time input')

        if len(errors) <1:
            thereferral.fixedDate = theDate
            thereferral.fixedTime = theTime
            thereferral.save()
            #send email to patient
            tasks.ref_appointment_email.delay(request, referralId)

            del request.session['referralId']
            return HttpResponseRedirect('/accounts/hospital_referrals/')

        else:

            return fix_referral(request, referralId, errors)

    else:
        return hospital_referrals(request)


