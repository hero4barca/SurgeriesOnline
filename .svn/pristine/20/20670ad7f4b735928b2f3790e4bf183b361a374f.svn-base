from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404, HttpResponseRedirect
from surgeriesOnline.forms import *
from surgeriesOnline.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from surgeriesOnline.modules.patientHistoryClass import *
from django.core.mail import send_mail
import datetime, re,time
from surgeriesOnline.view_dir.views import  success
from surgeriesOnline.tasks import *


def user_is_patient( user):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and user_profile.usertype =='patient'


@user_passes_test(user_is_patient,login_url="/accounts/login/")
def request_transfer(request):
    """
    request surgery transfer for a patient
    :param request: http request
    :return: httpresponse
    """
    if request.method == 'POST':
        form = TransferRequestForm(request.POST, request=request)
        if form.is_valid():
            cd = form.cleaned_data
            newPatientTransfer = PatientTransfer( patient=Patient.objects.get(userProfile__user= request.user),
                                                  fromSurgery_id=request.session['surgeryId'],
                                                  toSurgery_id= cd['toSurgery'].pk ,
                                                  requestDate= datetime.datetime.now().date(),
                                                  transferStatus=False)
            newPatientTransfer.save()
            success(request,
             message =''' Your already made payment for this prescription <a href='/accounts/profile/'> back</a>''')
            return HttpResponseRedirect('/accounts/profile/')

    else:
        form = TransferRequestForm(request=request)

    return render(request, 'patient/request_surgery_transfer.html', {'form':form})


@user_passes_test(user_is_patient,login_url="/accounts/login/")
def payment(request, prescriptionId):
    """
    payment for subcriptions
    :param request: http request
    :param prescriptionId: prescription Id
    :return: http response
    """
    try:
        oldPayment = Payment.objects.get(prescription_id=prescriptionId)
        return success(request,
             message =''' Your already made payment for this prescription <a href='/accounts/profile/'> back</a>''')

    except Payment.DoesNotExist:
        oldPayment = None


    if request.method == "POST":
        form = PresPaymentForm(request.POST, request=request)

        if form.is_valid(): # charges the card

            del request.session['prescriptionId']#delete the prescriptionId session

            send_payment_notification.delay(request,prescriptionId)# send relevant notifications

            return HttpResponseRedirect('/successful_payment/')

    else:
        request.session['prescriptionId'] = prescriptionId
        form = PresPaymentForm(request=request)

    return render(request, "patient/payment.html", {'form': form})


def successful_payment(request):
    return render(request,'patient/payment_success.html')


#allows patient to reject proposed referral appointment
@user_passes_test(user_is_patient,login_url="/accounts/login/")
def reject_ref_date(request, referralId):

    theReferral = Referral.objects.get(pk=referralId)
    theReferral.fixedDate = None
    theReferral.fixedTime = None
    theReferral.save()

    #send email to facility
    hospital_ref_appointment_mail.delay(request, referralId, False)

    #send email to patient
    patient_ref_appointment_mail.delay(request, referralId, False)

    return my_ref_details(request,referralId)


#allows patient to accept proposed referral appointment
@user_passes_test(user_is_patient,login_url="/accounts/login/")
def accept_ref_date(request, referralId):

    theReferral = Referral.objects.get(pk=referralId)
    theReferral.fixed = True
    theReferral.save()

    #send email to facility
    hospital_ref_appointment_mail.delay(request, referralId, True)

    #send email to patient
    patient_ref_appointment_mail.delay(request, referralId, True)
    return my_ref_details(request,referralId)


@user_passes_test(user_is_patient,login_url="/accounts/login/")
def my_ref_details(request, referralId):
    """
    display the details of a referral
    :param request: http request
    :param referralId: referral Id
    :return: http reponse
    """
    theReferral = Referral.objects.get(pk = referralId)
    return render(request, 'patient/my_ref_details.html', {'ref': theReferral})



@user_passes_test(user_is_patient,login_url="/accounts/login/")
def show_referrals(request):
    """
    shows a patien's referrals
    :return: http response
    """
    try:
        pendingReferrals = Referral.objects.filter(doctorAppointment__doctorBooking__patient__userProfile__user=request.user,
                                                   status = False)
    except Referral.DoesNotExist:
        pendingReferrals = None

    return render(request,
                  'patient/show_my_referrals.html', {'referrals': pendingReferrals})



@user_passes_test(user_is_patient,login_url="/accounts/login/")
def show_prescriptions(request):
    """
    shows a patients rescription pnding
    :return: http response
    """

    myPrescriptions = Prescription.objects.filter(doctorAppointment__doctorBooking__patient__userProfile__user= request.user,
                                                  deliveryStatus=0)
    return render (request,
                   'patient/show_my_prescriptions.html', {'myPrescriptions':myPrescriptions})


@user_passes_test(user_is_patient,login_url="/accounts/login/")
def show_medical_history(request):
    """
    displays a patient's medical history
    :return: http response
    """

    currentPatient = Patient.objects.get(userProfile__user = request.user)
    patientHistory = PatientHistory(currentPatient, request).computeHistory()


    return render(request,
                  'patient/show_my_history.html', {'medical_history': patientHistory,
                                                    'patientId': currentPatient.pk})



@user_passes_test(user_is_patient,login_url="/accounts/login/")
def get_patient_bookings(request, staffType):
    '''
    show bookings made by patient
    :param request:http request
    :param staffType: doctor or nurse
    :return: http response
    '''

    patientProfile = UserProfile.objects.get(user= request.user)
    thePatient = Patient.objects.get(userProfile=patientProfile)


    if staffType == 'doctor':
        try:
            bookings =  DoctorBooking.objects.filter(patient=thePatient,status=0)

            #filter by date - to ensure that prevent unattended bookings
            bookings =list(bookings)
            for b in bookings:
                b_date = b.doctorAvailability.date
                today= datetime.datetime.now().date()
                if b_date < today:
                    bookings.remove(b)

        except DoctorBooking.DoesNotExist:
            bookings = None
    else:
        try:

            bookings =  NurseBooking.objects.filter(patient=thePatient, status=0)
            bookings =list(bookings)

            for b in bookings:
                b_date = b.nurseAvailability.date
                today= datetime.datetime.now().date()
                if b_date < today:
                    bookings.remove(b)

        except NurseBooking.DoesNotExist:
            bookings = None

    return filter_bookings(bookings)




@user_passes_test(user_is_patient,login_url="/accounts/login/")
def show_appointment_date(request, staffType):
    '''
    shows patient appointment by date
    :param request: http request
    :param staffType: doctor or nurse
    :return: http response
    '''

    errors = []
    today = datetime.datetime.date(datetime.datetime.now()) #use to ensure that date not beyound current day
    if request.method == 'POST':

        if not request.POST.get('date',''):
            errors.append('no new date seleted')
        else:
            formDate = request.POST.get('date','')
            try:
                formDate = datetime.datetime.strptime(formDate, "%d-%b-%Y")
                formDate = datetime.datetime.date(formDate)
                #errors.append('Date is invalid')
            except :
                errors.append('invalid date input')

    if errors.__len__()>=1:
         return show_appointment(request,staffType=staffType,error=errors)
    else:
         return show_appointment(request, staffType= staffType, theDate=formDate)



def filter_bookings(bookings):
    """
    filter's a booking query set by date, removes past bookings
    :param bookings:  query set of bookings
    :return: pending bookings (query set)
    """

    #filter before returning
    pendingbookings = list(bookings)

    for b in bookings:
        if b.get_date() < datetime.datetime.now().date():
            pendingbookings.remove(b)


    return pendingbookings



def filter_time_slots(booking_slots):
    """
    filter's time slots
    :param booking_slots: booking slot (query set)
    :return: filtered slots - list
    """

    currentTime = datetime.datetime.time(datetime.datetime.now())
    filtered_slots = list(booking_slots)
    for slot in booking_slots:
        if  currentTime >= slot.get_timeslot():
            filtered_slots.remove(slot)

    return filtered_slots



@user_passes_test(user_is_patient,login_url="/accounts/login/")
def show_appointment(request, staffType ,
                                theDate= datetime.datetime.date(datetime.datetime.now()),error=None):
    """
    display available appointment slots for a given date
    :param request: htttp request
    :param staffType: nurse or doctor
    :param theDate: date
    :param error: form errors
    :return: http response
    """

    today = datetime.datetime.date(datetime.datetime.now())
    currentTime = datetime.datetime.time(datetime.datetime.now())


    mySurgery = Surgery.objects.get(pk=request.session['surgeryId'])
    if staffType== 'doctor':
        booking_slots = DoctorAvailability.objects.filter(surgery_id= mySurgery,
                                                      booked=False, date=theDate)
        templateName = 'patient/book_doc_appointment.html'
    else:
         booking_slots = NurseAvailability.objects.filter(surgery_id= mySurgery,
                                                      booked=False, date=theDate)
         templateName = 'patient/book_nurse_appointment.html'

    #get bookings already done by current patient
    myBookings = get_patient_bookings(request, staffType)


    #filter booking timeslot - if date is current day
    if theDate == today:
        booking_slots = filter_time_slots(booking_slots)

    return render(request, templateName, {'bookingslots': booking_slots,
                                                     'myBookings':myBookings,
                                                    'date': theDate,
                                                    'date_error': error})



@user_passes_test(user_is_patient,login_url="/accounts/login/")
def save_appointment(request,availability, staffType):
    """
    save an appointment booking
    :param request: http request
    :param availability: availability Id
    :param staffType: odctor or nurse
    :return: http response
    """

    patientProfile = UserProfile.objects.get(user= request.user)
    thePatient = Patient.objects.get(userProfile=patientProfile)

    mySurgery = Surgery.objects.get(pk=request.session['surgeryId'])
    if staffType=='doctor':
        booked_slot = DoctorAvailability.objects.get(pk=availability)
    else:
        booked_slot = NurseAvailability.objects.get(pk=availability)

    booked_slot.booked = True
    booked_slot.save()

    if staffType=='doctor':
        newBooking = DoctorBooking(doctorAvailability= booked_slot, surgery=mySurgery,
                                       patient= thePatient)
        newBooking.save()


        #notification emial
        booking_notification(request.user.email,True,booked_slot)


        return  HttpResponseRedirect('/accounts/doctor_appointment/')
    else:
        newBooking = NurseBooking(nurseAvailability=booked_slot, surgery=mySurgery,
                                       patient= thePatient)
        newBooking.save()

        #notification email
        booking_notification(request.user.email,True,booked_slot)

        return  HttpResponseRedirect('/accounts/nurse_appointment/')





@user_passes_test(user_is_patient,login_url="/accounts/login/")
def delete_booking(request,bookingId, staffType):
    """
    deletes a previosly made booking
    :param request: http request
    :param bookingId: booking Id
    :param staffType: doctor or nurse
    :return: http response
    """
    # retrieve patient
    patientProfile = UserProfile.objects.get(user= request.user)
    thePatient = Patient.objects.get(userProfile=patientProfile)

    mySurgery = Surgery.objects.get(pk=request.session['surgeryId'])

    if staffType == 'doctor':

        try:

            booking = DoctorBooking.objects.get(pk=bookingId)
            booked_slot = DoctorAvailability.objects.get(pk=booking.doctorAvailability.pk_val())
            booked_slot.booked = False
            booked_slot.save()
            booking.delete()

            #send email notification
            booking_notification(request,False, booked_slot)

        except DoctorBooking.DoesNotExist:
            return  HttpResponseRedirect('/accounts/doctor_appointment/')


        return  HttpResponseRedirect('/accounts/doctor_appointment/')
    else:
        booking = NurseBooking.objects.get(pk=bookingId)
        booked_slot = NurseAvailability.objects.get(pk=booking.nurseAvailability.pk_val())
        booked_slot.booked = False
        booked_slot.save()
        booking.delete()

        #send email notification
        booking_notification.delay(request,False, booked_slot)

        return  HttpResponseRedirect('/accounts/nurse_appointment/')



