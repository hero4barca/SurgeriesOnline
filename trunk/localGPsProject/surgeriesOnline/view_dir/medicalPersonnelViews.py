from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import send_mail
from surgeriesOnline.forms import *
from surgeriesOnline.modules.patientHistoryClass import *
from surgeriesOnline.modules.schCalendarClass import *
from surgeriesOnline import tasks
import re

def user_is_medicalPersonnel(user):
    '''
    :param user:
    :return: True is user is nurse or doctor
    '''
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and user_profile.usertype =='doctor' or user_profile.usertype =='nurse'


def user_is_doctor(user):
    '''
    :param user:
    :return: True is user is doctor; False
    '''
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and user_profile.usertype =='doctor'


def user_is_nurse(user):
    '''
    :param user:
    :return: True if user is nurse; False
    '''
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and  user_profile.usertype =='nurse'


@user_passes_test(user_is_doctor, login_url="/accounts/login/")
def doctor_previous_appointments(request):
    """
    Function queries the previous or closed appointments for the current user
    :return: HTTP request to a page displaying the apointments  and details
    """
    profile= UserProfile.objects.get(user=request.user)

    try:
        previousAppointment= DoctorAppointment.objects.filter(doctorBooking__doctorAvailability__doctorId__userProfile = profile,
                                                             doctorBooking__status=1).order_by('-doctorBooking__doctorAvailability__date')
    except DoctorAppointment.DoesNotExist:
        previousAppointment = None


    return render(request, 'doctor/doctor_previous_appointments.html', {'appointments': previousAppointment})




@user_passes_test(user_is_nurse, login_url="/accounts/login/")
def nurse_previous_appointments(request):
    """
    Function queries the previous and closed appoiontemnts for the current user
    :return: HTTP request to a page displaying the appointmets and details
    """
    profile= UserProfile.objects.get(user=request.user)

    try:
        previousAppointment = NurseAppointment.objects.filter(nurseBooking__nurseAvailability__nurseId__userProfile = profile,
                                                              nurseBooking__status=1).order_by('-nurseBooking__nurseAvailability__date')

    except NurseAppointment.DoesNotExist:
        previousAppointment = None

    return render(request, 'nurse/nurse_previous_appointments.html', {'appointments': previousAppointment})



@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def close_completed_appointment(request, bookingId, staffType):
    '''
    closes a booked appointment that has been completed
    changes the status of an appointment form '0' to '1'
    :param request:
    :param bookingId:
    :param staffType: 'doctor' or 'nurse'
    :return:
    '''

    if staffType == 'doctor':
        theBooking = DoctorBooking.objects.get(pk= bookingId)
        theBooking.status= 1
        theBooking.save()
        return HttpResponseRedirect('/doctor_accounts/booked_appointment/')
    else:
        theBooking = NurseBooking.objects.get(pk= bookingId)
        theBooking.status= 1
        theBooking.save()
        return HttpResponseRedirect('/nurse_accounts/booked_appointment/')




#save the details of an appointment or consultation with a patient
@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def save_patient_appointment(request, staffType):
    """
    saves the datails of a patient appointment
    :param request: http request
    :param staffType:
    :return:
    """
    bookingId = int(request.session['bookingId'])
    if request.method=='POST':
        form = PatientConsultationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if staffType == 'doctor':
                #create  appointment
                theAppointment = DoctorAppointment.objects.create(doctorBooking_id= bookingId,
                                                                  details = cd['consultationDetails'],
                                                                  surgery = Surgery.objects.get(name= request.session['userSurgery']) )
                theAppointment.save()

                #create prescription
                if cd['prescription']:
                    newPrescription = Prescription.objects.create(doctorAppointment = DoctorAppointment.objects.get(doctorBooking_id=bookingId),
                                                                  surgery = Surgery.objects.get(name= request.session['userSurgery']),
                                                                  paymentStatus=False, deliveryStatus=False,
                                                                  details = cd['prescriptionDetails'])
                    newPrescription.save()
                #create referral
                if cd['referral']:
                    newReferral = Referral.objects.create(doctorAppointment = theAppointment,
                                                          surgery = Surgery.objects.get(name= request.session['userSurgery']),
                                                          specializedFacility= cd['referralFacilityName'], status=False,
                                                          details= cd['referralDetails'])
                    newReferral.save()
                    tasks.sendReferralNotification.delay(request,newReferral.pk)#send notification email for referrals


                del request.session['bookingId']

                return HttpResponseRedirect('/doctor_accounts/booked_appointment/')
            else:
                theAppointment = NurseAppointment.objects.create(nurseBooking_Id = bookingId,
                                                                details = cd['consultationDetails'],
                                                                surgery = Surgery.objects.get(name= request.session['userSurgery']) )
                theAppointment.save()

                del request.session['bookingId']

                return HttpResponseRedirect('/nurse_accounts/booked_appointment/')

        else:
            return current_patient_appointment(request, bookingId,staffType, form)
    else:
        return current_patient_appointment(request,bookingId, staffType)



#display the consultation page - Patient history, presciption , referral , appointment forms
@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def current_patient_appointment(request,bookingId, staffType, form=None):
    """
    presents a consultation form to a clinical staff who is currently consulting with a patient
    :param request:
    :param bookingId: booking id
    :param staffType: user staff type
    :param form: consultation form
    :return: http request
    """

    if form ==None:
        form = PatientConsultationForm()

        #retrieve patient history and display here
    if staffType == 'doctor':
        currentPatient = DoctorBooking.objects.get(pk=bookingId).patient
        currentPatientHistory = PatientHistory(currentPatient,request).computeHistory()
        templateName = 'doctor/doctor_consultation.html'
    else:
        currentPatient = NurseBooking.objects.get(pk=bookingId).patient
        currentPatientHistory = PatientHistory(currentPatient, request).computeHistory()
        templateName = 'nurse/nurse_consultation.html'


        # save the appointmentId in a session object
    request.session['bookingId'] = bookingId
    #assert False

    return render(request,templateName , {'form': form,
                                                       'staffType': staffType,
                                                       'patient':currentPatient ,
                                                       'patient_History': currentPatientHistory})




#diaplays booking made by patients starting from the given date
@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def my_patient_booking_date(request, staffType):
    """
    queries patient booking for a doctor or nurse from a selected date
    :param request: http request
    :param staffType: staff type i.e. doctor or nurse
    :return: http request
    """
    errors = []
    today = datetime.datetime.date(datetime.datetime.now()) #use to ensure that date not beyound current day
    if request.method == 'POST':

       if not request.POST.get('date',''):
            errors.append('no new date selected')
       else:
            formDate = request.POST.get('date','')
            try:
                formDate = datetime.datetime.strptime(formDate, "%d-%b-%Y")
                formDate = datetime.datetime.date(formDate)
                #errors.append('Date is invalid')
            except :
                errors.append('invalid date input')

    if errors.__len__()>=1:
          return my_patient_booking(request, staffType=staffType, error=errors)
    else:
          return my_patient_booking(request, staffType=staffType, theDate=formDate, error=errors)




#diaplay bookings made by patients starting from today
@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def my_patient_booking(request, staffType,  theDate= datetime.datetime.today().date(),
                                    error =None):
    """
    queries patient booking for a staff from the current date
    :param request: http request
    :param staffType: staff type i.e. doctor or nurse
    :param theDate: date
    :param error: form errors
    :return: http request
    """

    if staffType == 'doctor':
        templateName = 'doctor/doctor_booked_appointments.html'
        myBookings = DoctorBooking.objects.filter(doctorAvailability__doctorId__userProfile__user =request.user,
                                                      doctorAvailability__booked=True, status=False).order_by('doctorAvailability__timeSlot')
    else:
        templateName = 'nurse/nurse_booked_appointments.html'
        myBookings = NurseBooking.objects.filter(nurseAvailability__nurseId__userProfile__user =request.user,
                                                      nurseAvailability__booked=True ,status=False).order_by('nurseAvailability__timeSlot')
    listBookings = list(myBookings)
    pending_bookings = []
    #filter by date - remove past


    for book in listBookings:
        if not book.get_date()< theDate:
            pending_bookings.append(book)



    return render(request,templateName , {'pending_bookings': pending_bookings,
                                          #'closed_bookings' : listBookings.filter(status=1),
                                                          'date': theDate,
                                                            'today': datetime.datetime.today().date(),
                                                            'date_error': error})



@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def myScheduleCalendar(request):
    """
    displays the schedule calendar from the current month
    :param request: http request
    :return: http request
    """
    cal = MonthScheduleCalendar(request,datetime.datetime.now())
    return render(request, 'mySchedule.html', {'Calendar': cal

                                               })


@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def prevOrNextScheduleCalendar(request,year, month):
    """
    displays the schedule calendar of a next or previous month
    :param request: http request
    :param year: year (yyyy)
    :param month: month (mm)
    :return: http request
    """
    cal = MonthScheduleCalendar(request,datetime.datetime(int(year),int(month),1))
    return render(request, 'mySchedule.html', {'Calendar' :cal })



# delete availability for a given day
@user_passes_test(user_is_medicalPersonnel,login_url="/accounts/login/")
def delete_day(request, year, month, day):
    """
    delete a staff's availability for a given day
    :param request: http request
    :param year: year (yyyy)
    :param month: month (mm)
    :param day: day
    :return: call - prevOrNextScheduleCalendar
    """

    thedate = datetime.date(year= int(year), month=int(month), day=int(day))

    if request.session['usertype']== 'doctor':
       dateSlots = DoctorAvailability.objects.filter(date=thedate,
                                                           doctorId__userProfile__user= request.user)
    else:
        dateSlots = NurseAvailability.objects.filter(date=thedate,
                                                           nurseId__userProfile__user= request.user)

    for slot in dateSlots:
            slot.delete()

    return prevOrNextScheduleCalendar(request,year, month)



#saves the schedule from form the month schedule calendar
def save_schedule(request):
    """
    saves staff's availabilty
    :param request: http request
    :return: call - prevOrNextScheduleCalendar
    """

    if request.method == 'POST':
        dates = request.POST


    staffPofile = UserProfile.objects.get(user= request.user)
    if staffPofile.usertype == "doctor":
        staff =Doctor.objects.get(userProfile=staffPofile)
        usertype = "doctor"
    else:
        staff =Nurse.objects.get(userProfile=staffPofile)
        usertype = "nurse"

    userSurgery = Surgery.objects.get(name=request.session['userSurgery'])

    for d in dates.values():
        dSplit= re.split('/', d)
        if len(dSplit) ==3:
            dt  = datetime.date(year= int(dSplit[2]), month= int(dSplit[1]), day= int(dSplit[0]))
            update_schedule(staff,userSurgery,dt,usertype)

    return prevOrNextScheduleCalendar(request, year=dt.year, month=dt.month)


#adds time by 30mins
def time_plus(time, timedelta):
    """
    adds give number of minutues to a given time in correct time format
    :param time: time
    :param timedelta: minutes in time slot
    :return: end i.e. time + timedelta
    """
    start = datetime.datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()


def update_schedule( staff, surgery, date, usertype,
                     start_time =datetime.time(8,0), stop_time = datetime.time(18,0)):
    """

    :param staff: staff
    :param surgery: surgery
    :param date: date
    :param usertype: staff type i.e. doctor or nurse
    :param start_time: start time - start of daily schedule
    :param stop_time: stop time - end  of daily schedule
    :return: None
    """

    slot = start_time

    if usertype == "doctor":
         while (slot < stop_time):
            newDocAvailability = DoctorAvailability(doctorId= staff, surgery= surgery,
                                                       date= date,timeSlot=slot,booked=False)
            newDocAvailability.save()
            slot = time_plus(slot, datetime.timedelta(minutes= 30))
    else:
         while (slot < stop_time):
            newNurAvailability = NurseAvailability(nurseId=staff, surgery= surgery,
                                                       date= date,timeSlot=slot,booked=False)
            newNurAvailability.save()
            slot = time_plus(slot, datetime.timedelta(minutes= 30))
