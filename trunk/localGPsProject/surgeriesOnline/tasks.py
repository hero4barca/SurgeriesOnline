from __future__ import absolute_import

from celery.task import *
from  celery.schedules import crontab
from celery import shared_task

import  datetime
from django.core.mail import send_mail
from surgeriesOnline.models import *
from django.http import HttpResponse



@shared_task
def test():

    subject= "Reminder: Doctor's appointment today"
    message = 'This is a reminder for you doctors appointment today.\n' \
                  'Time: '  +'\n'
    message = message + 'Please remember to be on time and cancel the appointment if you are unable to meet up'
    message = message + 'Please contact you surgery for any enquires'

    fromEmail = settings.EMAIL_HOST_USER

    #fromEmail = "referrals@surgeriesOnline.com"

    send_mail(subject,message,fromEmail,['ie36@student.le.ac.uk'])

    return

@shared_task()
def sendReferralNotification(request,referalId):
    """
    Sends notification email after a referral has been made to the patient and the hospital
    :param request: HTTP request
    :param referalId: referral id
    :return: None
    """

    theReferral = Referral.objects.get(pk=referalId)
    surgery = theReferral.surgery
    referredFacility = Referral.specializedFacility
    facilityUser = referredFacility.user


    theAppointment = theReferral.doctorAppointment
    thePatient = theAppointment.doctorBooking.patient

    subject = 'Referral Notification from' + str(request.session['userSurgery'])
    message = 'Patient ' + thePatient.get_name() + ' has been referral to your facility from ' + str(request.session['userSurgery'])+'\n'
    message = message+ 'Referred by Doctor ' + str(theAppointment.get_doctor()) + ', on ' + str(theAppointment.get_date()) +' for the reasons below\n'
    message = message+ 'REFERRAL DETAILS: \n' + str(theReferral.details) +'\n' + "DOCTOR'S APPOINTMENT DETAILS\n" + str(theAppointment.details) +'\n'
    message = message+ "The patient's contact details are displayed below \n" + " email: " + str(thePatient.userProfile.get_email()) +'\n'
    message = message+ "phone No: " + str(thePatient.phoneNo) + '\n '
    message = message+ "The patient's history is accessible from the surgeriesOnline portal \n \n"
    message = message+ "This referral is from " + str(request.session['userSurgery'])
    message = message+"\n Thank you"

    surName = request.session['userSurgery']
    surName.replace(" ", "")
    fromEmail = 'referrals_' + surName +'@surgeriesOnline.com'
    send_mail(subject, message, fromEmail , [facilityUser.email])

    message =  'You have been referred to ' + str(referredFacility.name) + ' by Doctor ' + str(theAppointment.get_doctor())
    message = message+ ' on ' + str(theAppointment.get_date()) +'. Please check your account for more details.'

    patientUser = thePatient.userProfile.user
    send_mail(subject, message, fromEmail,[patientUser.email])
    return


#send email notification for referral appointment
@shared_task()
def ref_appointment_email(request, referralId):

    theReferral = Referral.objects.get(pk = referralId)
    theAppointment = theReferral.doctorAppointment
    thePatient = theAppointment.doctorBooking.patient

    patientUser = thePatient.userProfile.user

    subject = 'Referral appointment notification'
    message = 'This is a notification of referral appointment.\n'
    message = message + 'Date: ' + str(theReferral.fixedDate) +'\n'
    message = message+ 'Time: ' + str(theReferral.fixedTime) +  '\n'

    message = message+ 'REFERRAL DETAILS:\n'
    message = message+ str(theReferral.details)

    message =message + 'Please login to you account to confirm or decline the appointment'

    facility =  theReferral.specializedFacility
    faciUser = facility.user
    fromEmail = faciUser.email

    send_mail(subject, message, fromEmail,[patientUser.email])
    return

@shared_task()
def prescription_delivery_mail(prescriptionId, patientEmail):

    thePrescription = Prescription.objects.get(pk=prescriptionId)

    subject = 'Notification of prescription dispatch '
    emailMsg = 'This message is a confirmation that your prescription detailed below has been dispatched for delivery' \
                                                         ' ' + str(thePrescription.details) +' amount' + str(thePrescription.price) +'\n' \
                                                         'time:' + str(datetime.now())
    emailMsg = emailMsg + '\n Thank You'

    fromEmail = 'noreplyPharmacy_@surgeriesOnline.com'

    send_mail(subject,emailMsg,fromEmail,[patientEmail])


@shared_task()
def patient_ref_appointment_mail(request, referralId, action):

    theReferral = Referral.objects.get(pk = referralId)

    if not action:
        subject = "Referral appointment slot canceled"
        message = "This is a notification that the  the proposed" \
                        "slot for the referral appointment you rejected has been cancelled\n"
        message = message+ str(theReferral.fixedDate) +', ' +str(theReferral.fixedTime) +'\n'
        message= message+ 'REFERRAL DETAILS: ' + theReferral.details
    else:
        subject = "Confirmation of referral appointment "
        message = "This is to confirm that your referral appointment has been fixed for : \n"

        message = message + str(theReferral.fixedDate) +', ' +str(theReferral.fixedTime) +'\n'
        message=  message+ 'REFERRAL DETAILS: ' + theReferral.details

    fromEmail = "referralnotifications@surgeriesOnline.com"
    send_mail(subject,message, fromEmail,[request.user.email])
    return

@shared_task()
def hospital_ref_appointment_mail(request, referralId, action):

    theReferral = Referral.objects.get(pk=referralId)

    if not action:
        subject = 'Notification of appointment cancelation'
        message = 'This is a notice that the patient' +str(request.user.get_full_name) + "has rejected the proposed" \
                        "slot for the referral appointment\n"
        message = message + str(theReferral.fixedDate) +', ' +str(theReferral.fixedTime) +'\n'
        message= message + 'REFERRAL DETAILS: ' + theReferral.details
    else:
        subject = 'Notification of appointment confirmation'
        message = 'This is to confirm that the patient' +str(request.user.get_full_name) + "has accepted the proposed" \
                    "slot for the referral appointment\n"
        message = message + str(theReferral.fixedDate) +', ' +str(theReferral.fixedTime) +'\n'
        message=message + 'REFERRAL DETAILS: ' + theReferral.details


    fromEmail = 'referralnotification@surgeriesOnline.com'

    faciUser =theReferral.specializedFacility.user
    send_mail(subject,message, fromEmail,[faciUser.email])
    return

@shared_task()
def send_payment_notification(request, prescriptionId):
    """
    send successful payment notification
    :param request: http request
    :param prescriptionId: prescription Id
    :return: http response
    """

    thePrescription = Prescription.objects.get(pk=prescriptionId)

    subject = 'Confirmation of prescription payment'
    emailMsg = 'This message is a confirmation that  payment was successful \n'
    emailMsg = emailMsg + ' We will contact you shortly to arrange deliiver or collection of your prescription'

    fromEmail = 'pharmacy_' + request.session['userSurgery']+'@surgeriesOnline.com'

    #send email to patient
    send_mail(subject,emailMsg, fromEmail,[request.user.email])

    thePharmacy = Pharmacy.objects.get(surgery__name= request.session['userSurgery'],
                                       surgery_id= request.session['surgeryId'])
    pharmUser =thePharmacy.userProfile.user


    subject = 'Confirmation of prescription payment by ' +  str(request.user.get_full_name())
    emailMsg = 'This message is a confirmation that  patient' \
               ' ' +  str(request.user.get_full_name()) +'has successfully made payment for the prescription detailed below: \n' \
                                                         ' ' + str(thePrescription.details) +' amount' + str(thePrescription.price)
    emailMsg = emailMsg + 'The payment has been credited. \n Thank You'

    fromEmail = 'noreply_payments@surgeriesOnline.com'
    #send email to pahrmacy
    send_mail(subject,emailMsg, fromEmail,[pharmUser.email])

    return


@shared_task()
def booking_notification(toEmail,action, booked_slot):
    """
    email notifications for new bookings and cancelations
    :param request: http request
    :param action: new booking - True; booking cancelation - False
    :param booked_slot: booked slot
    :return:
    """

    if action:
        subject = 'New appointment confirmation'
        emailMsg = 'This message is a confirmation of your booking for'+ str(booked_slot.timeSlot) + 'on ' + str(booked_slot.date) + '/n'
        emailMsg = emailMsg + 'Please remember to cancel the appointment if you cannot attend'
    else:
        subject = 'Confirmation of canceled appointment'
        emailMsg = 'This message is a confirmation that your booking for'+ str(booked_slot.timeSlot) + 'on ' + str(booked_slot.date) + ' has been cancelled /n'
        emailMsg = emailMsg + 'Please feel free to book another appointment when you are ready.'

    fromEmail = 'noreply_notifications@surgeriesOnline.com'

    send_mail(subject,emailMsg, fromEmail,[toEmail])



@shared_task()
def send_reg_mail_surgery(surgeryName, regNo, userName, firstname, lastname, email):

    subject = 'Confirmation of surgery registration'

    message = "This is a confirmation that you successfully registered a surgery with Surgeries Online \n "
    message = message + "You registered: " + str(surgeryName) + "\n Registration number: " + str(regNo) +"\n"
    message = message + "Admin user details\n"
    message = message + "Admin username: " + str(userName) + "\n"
    message = message + "Name: " + firstname +  " " + lastname + "\n"

    message = message + "You are welcome to Surgeries Online.\n"

    fromEmail = 'noreply@surgeriesOnline.com'

    send_mail(subject, message,fromEmail, [email])


@shared_task()
def send_reg_mail_patient(surgeryName, NHS_No, userName, email):

    subject = 'Confirmation of patient registration'

    message = "This is a confirmation that you successfully signed up as a patient on Surgeries Online \n "
    message = message + "Surgery " + str(surgeryName) + "\n NHS-number: " + str(NHS_No) +"\n"

    message = message + " username: " + str(userName) + "\n"

    message = message + "You are welcome to Surgeries Online.\n"

    fromEmail = 'noreply@surgeriesOnline.com'

    send_mail(subject, message,fromEmail, [email])


@shared_task()
def send_reg_mail_specFaci(hospitalName, username, email):

    subject = "Confirmation of hospital registration"

    message = "This is to confirm that the hospital " + str(hospitalName) + "has been registered \n"
    message = message + "Admin username" + str(username) +"\n"

    message = message + "Thank You for joining Surgeries Online"

    fromEmail = "noreply@surgeriesOnline.com"

    send_mail(subject, message, fromEmail, [email])




@shared_task()
def send_new_account_mail(theUsername, theUserEmail, theUsertype,theUserSurgeryName, password):

    subject = "Surgeries Online Account"

    message = "Your online SurgeriesOnline account has been successfully setup \n"
    message = message + "You are registered as a " + str(theUsertype) + " with " + str(theUserSurgeryName) + "\n"
    message = message + "username: " + str(theUsername) + "\n"
    message = message + "password: " + password + "\n"
    message = message + "Please change this password once you login"

    fromEmail = "noreply@surgeriesOnline.com"

    send_mail(subject,message,fromEmail,[theUserEmail])


#@periodic_task(run_every=crontab(hour=12, minute=10, day_of_week=1))
def send_daily_notification():
    today = datetime.datetime.now().date()

    #for bookings with doctors
    try:
        todayDocBookings = DoctorBooking.objects.filter( doctorAvailability__date= today)
        send_doc_booking_reminder(todayDocBookings)

    except DoctorBooking.DoesNotExist:
        todayDocBookings = None

    #for bookings with nurses
    try:
        todayNurseBookings = NurseBooking.objects.filter(nurseAvailability__date= today)
        send_nur_booking_reminder(todayNurseBookings)
    except NurseBooking.DoesNotExist:
        todayNurseBookings = None

    return #HttpResponse('Notifications despatched')


def send_doc_booking_reminder(todayBookings):

    for booking in todayBookings:
        thePatient = booking.patient
        patientUserEmail = thePatient.userProfile.get_email()

        subject= "Reminder: Doctor's appointment today"
        message = 'This is a reminder for you doctors appointment today.\n' \
                  'Time: ' + str(booking.doctorAvailability.timeSlot) +'\n'
        message = message + 'Please remember to be on time and cancel the appointment if you are unable to meet up'
        message = message + 'Please contact you surgery for any enquires'

        fromEmail = 'noreply_notifications@surgeriesOnline.com'


        send_mail(subject,message,fromEmail,[patientUserEmail])

    return


def send_nur_booking_reminder(todayBookings):

    for booking in todayBookings:
        thePatient = booking.patient
        patientUserEmail = thePatient.userProfile.get_email()

        subject= "Reminder: Doctor's appointment today"
        message = 'This is a reminder for you doctors appointment today.\n' \
                  'Time: ' + str(booking.nurseAvailability.timeSlot) +'\n'
        message = message + 'Please remember to be on time and cancel the appointment if you are unable to meet up'
        message = message + 'Please contact you surgery for any enquires'

        fromEmail = 'noreply_notifications@surgeriesOnline.com'

        send_mail(subject,message,fromEmail,[patientUserEmail])

    return