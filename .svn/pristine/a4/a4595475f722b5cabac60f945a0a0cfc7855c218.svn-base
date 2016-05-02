from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from decimal import *
import datetime
from surgeriesOnline.forms import *
from django.core.mail import send_mail
from surgeriesOnline import tasks

def user_is_pharmacyUser(user):
    try:
        userProfile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and userProfile.usertype =='pharmacy'


# for displaying all new and prnding prescriptions to the pahrmacy account
@user_passes_test(user_is_pharmacyUser,login_url="/accounts/login/")
def pending_prescriptions(request):
    """
    displays pending prescriptions
    :param request: http request
    :return: http response
    """

    pendingPrescriptions = Prescription.objects.filter( surgery= Surgery.objects.get(name=request.session['userSurgery']),
                                                         deliveryStatus=False)

    return render (request, 'pharmacy/pharm_pending_prescriptions.html', {'prescriptionList': pendingPrescriptions})

#for setting the price of a prescription by a pahrmacy
@user_passes_test(user_is_pharmacyUser,login_url="/accounts/login/")
def set_prescription_price(request, prescriptionId):
    """
    sets price for prescriptions
    :param request: http request
    :param prescriptionId: prescription Id
    :return: http response
    """
    thePrescription = Prescription.objects.get(pk=prescriptionId)
    request.session['prescription'] = prescriptionId

    return render(request, 'pharmacy/set_prescription_price.html', {'prescription': thePrescription
                                                                                          })
@user_passes_test(user_is_pharmacyUser,login_url="/accounts/login/")
def save_prescription_price(request):
    """
    saves prescription price
    :param request: http request
    :return: http response
    """
    prescriptionId = request.session['prescription']
    errors =[]

    if request.method=='POST':

        if not request.POST.get('price',''):
            errors.append('No price entered')
        else:
            #assert False
            price = request.POST.get('price','')
            price = Decimal(price)


            if not price == None:
                thePrescription = Prescription.objects.get(pk=prescriptionId)
                thePrescription.price = price
                thePrescription.save()
            else:
                errors.append('price invalid')

    return pending_prescriptions(request)


@user_passes_test(user_is_pharmacyUser,login_url="/accounts/login/")
def make_prescription_delivery(request, prescriptionId):
    """
    dispatches prescription for delivery
    :param request: http request
    :param prescriptionId: prescription Id
    :return: http response
    """

    thePrescription = Prescription.objects.get(pk=prescriptionId)
    thePrescription.deliveryStatus = True
    thePrescription.save()

    prescriptionAppointment = thePrescription.doctorAppointment
    thebooking = prescriptionAppointment.doctorBooking
    thePatient = thebooking.patient

    patientUser =thePatient.userProfile.user

    #send email notification
    tasks.prescription_delivery_mail.delay(prescriptionId,patientUser.email)

    return pending_prescriptions(request)