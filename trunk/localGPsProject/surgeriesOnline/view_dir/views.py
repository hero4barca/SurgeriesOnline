from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,Http404, HttpResponseRedirect
from surgeriesOnline.forms import *
from surgeriesOnline.models import *
from surgeriesOnline.modules.patientHistoryClass import *
from surgeriesOnline.modules.ReportGeneratorClass import *
from reportlab.platypus.doctemplate import SimpleDocTemplate
from django.core.mail import send_mail

import datetime

from surgeriesOnline import tasks

def user_access_history(user):
    '''
    :param user:
    :return: True is user is nurse or doctor
    '''
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    return user.is_authenticated() and user_profile.usertype =='doctor' or user_profile.usertype =='nurse' or user_profile.usertype =='patient'

def test_celery(request):
    result = tasks.test.delay()
    #return HttpResponse(result.task_id)
    #assert  False
    return HttpResponse(result.task_id)



def index(request):
    """
    displays index page
    :param request: http request
    :return: http request
    """
    return render(request, 'index.html', )

def contact(request):
    """
    function display contact form on contact page
    :param request: http request
    :return: http request
    """

    if request.method =='POST':
        form = ContactForm(request.POST)

        if form.is_valid():

            cd = form.cleaned_data

            name = cd['name']
            email = cd['email']
            message = cd['message']

            if 'subject' in cd :
                subject = cd['subject']
            else:
                subject = 'subject'

            message = message + '\n Sent by ' + name + '\n'

            send_mail(subject, message, email, ['ie36@student.le.ac.uk'])

            return HttpResponseRedirect('/contact_email_sent/')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def project_details(request):
    """
    displays poject page
    :param request: http request
    :return: http request
    """
    return render(request,'project.html')


def register_surgery(request):
    """
    registers a patient with a surgery , unrestricted access
    :param request: http request
    :return: http request
    """
    if request.method == 'POST':
        form = SurgeryRegistrationForm(request.POST)

        if form.is_valid():

            cd = form.cleaned_data
            #update model

            newAdminUser = User.objects.create_user(username=cd['adminUsername'],email=cd['adminEmail'],
                                                 password=cd['adminPassword'], first_name=cd['adminFirstname'],
                                                 last_name=cd['adminLastname']
                                                 )
            newAdminUser.save()

            #create surgery
            newSurgery = Surgery(name= cd['surgeryName'], address= cd['surgeryAddress'], regNo= cd['regNo'])
            newSurgery.save()

            #create UserProfile
            newUserProfile = UserProfile(usertype='surgeryAdmin', user=newAdminUser, surgery=newSurgery)
            newUserProfile.save()

            #create surgery administrator
            newAdminUser = SurgeryAdmin(userProfile=newUserProfile, surgery=newSurgery, staffId=cd['adminStaffId'])
            newAdminUser.save()

            #send notification email
            tasks.send_reg_mail_surgery.delay(cd['surgeryName'],cd['regNo'],
                                              cd['adminUsername'],cd['adminFirstname'],cd['adminLastname'],
                                              cd['adminEmail'] )

            return  HttpResponseRedirect('/register/success/')
    else:
        form = SurgeryRegistrationForm()

    return render(request, 'register_surgery.html', {'form': form})



def register_patient(request):
    """
    registration of patients witha surgery, unrestricted access
    :param request: http request
    :return: http request
    """

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # update model

            #crete user objec
            newPatientUser = User.objects.create_user(username=cd['username'],email=cd['email'],
                                                      password=cd['password'], first_name=cd['firstname'],
                                                      last_name=cd['lastname'])
            newPatientUser.save()

            #create userProfile
            newPatientProfile = UserProfile(user=newPatientUser, usertype='patient', surgery=cd['surgery'])
            newPatientProfile.save()

            #create patient object
            newPatient = Patient(userProfile=newPatientProfile, surgery=cd['surgery'],address=cd['address'],
                                 phoneNo=cd['phoneNo'], NHS_No=cd['NHSno'])
            newPatient.save()

            #send email
            tasks.send_reg_mail_patient.delay(cd['surgery'].name,cd['NHSno'],cd['username'],email=cd['email'])

            #redirect for success
            return  HttpResponseRedirect('/register_patient/success/')
    else:
        form = PatientRegistrationForm()
    return render (request, 'register_patient.html', {'form': form})




def register_specializedFacility(request):
    """
    register a hospital or specialized facility
    :param request: http request
    :return: http request
    """

    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            newFacilityUser =  User.objects.create_user(username=cd['username'],email=cd['email'],
                                                      password=cd['password'])
            newFacilityUser.save()


            newFacility = SpecializedFacility(name= cd['hospitalName'], address=cd['address'],
                                               phoneNo=cd['phoneNo'], user= newFacilityUser)
            newFacility.save()

            #send mail
            tasks.send_reg_mail_specFaci(cd['hospitalName'],cd['username'],cd['email'])

            return  HttpResponseRedirect('/register_hospital/success/')
    else:
        form = HospitalRegistrationForm()
    return render (request, 'register_hospital.html', {'form': form})




#calls appropriate user account login function
@login_required(login_url="/accounts/login/")
def userAccountHome(request):
    """
    handles newly authenticated user
    :param request:
    :return:
    """
    try:
        specFaciUser = SpecializedFacility.objects.get(user= request.user)
        return specialzedFacilityUserAccountHome(request)

    except SpecializedFacility.DoesNotExist:
        return surgeryUserAccountHome(request)


# handles profile setup for surgery users
@login_required(login_url="/accounts/login/")
def surgeryUserAccountHome(request):
    #handles surgery user newly logged in
    #create user sessions if it doesn't already exist
    currentUserProfile = UserProfile.objects.get(user=request.user)

    if 'usertype' not in request.session:

        request.session['usertype'] = currentUserProfile.usertype
        request.session['userSurgery']= currentUserProfile.surgery.__str__()
        request.session['surgeryId'] = currentUserProfile.surgery_id

    if currentUserProfile.usertype == 'doctor':
        surgeryUser = Doctor.objects.get(userProfile=currentUserProfile)
    elif currentUserProfile.usertype == 'nurse':
        surgeryUser = Nurse.objects.get(userProfile=currentUserProfile)
    elif currentUserProfile.usertype == 'patient':
        surgeryUser = Patient.objects.get(userProfile=currentUserProfile)
    elif currentUserProfile.usertype == 'surgeryAdmin':
        surgeryUser = SurgeryAdmin.objects.get(userProfile=currentUserProfile)
    else:
        surgeryUser = Pharmacy.objects.get(userProfile=currentUserProfile)

    return render(request, 'userPage.html', {'profile': currentUserProfile,
                                                'surgeryUser':surgeryUser})

@login_required(login_url="/accounts/login/")
def specialzedFacilityUserAccountHome(request):
    """
    handles login for hospital admins
    :param request: http request
    :return: http request
    """

    specFaciUser = SpecializedFacility.objects.get(user= request.user)

    if 'facilityName' not in request.session:
        request.session['facilityName'] = specFaciUser.name

    return render (request, 'hospital/hospitalPage.html', {'facility': specFaciUser,
                                                  'today': datetime.datetime.now()})


def userAccountLogout(request):
    return render(request, 'success.html', {'event': 'logged out'})


#show the user accounts settings page
@login_required(login_url="/accounts/login/")
def my_account(request):
    """
    user account settings
    :param request: http request
    :return: http request
    """
    transfer = None
    if request.session['usertype']== 'patient':
        try:

            transfer =PatientTransfer.objects.get(patient__userProfile__user= request.user,transferStatus= False)

        except PatientTransfer.DoesNotExist:
           transfer = None


    return render(request, 'user_account_settings.html',{'transfer': transfer})


#for users to change their passwords from settings
@login_required(login_url="/accounts/login/")
def user_change_password(request):
    """
    handles password change
    :param request: http request
    :return: http request
    """
    errors = []

    #form = PasswordResetForm(user=request.user)
    if request.method == 'POST':

        if not request.POST.get('current',''):
            errors.append('please enter current password')
        else:
            current = request.POST.get('current','')

        if not request.POST.get('new', ''):
            errors.append('please enter new password')
        else:
            new = request.POST.get('new','')

        if not request.POST.get('newRepeat',''):
            errors.append('please enter repeat passord')
        else:
            newRepeat = request.POST.get('newRepeat','')

        if len(errors) < 1:
            if not request.user.check_password(current):
                errors.append('incorrect input for current password ')

            if not new == newRepeat:
                errors.append('password and password repeat do not match')

        if len(errors) <1:
            request.user.set_password(new)
            return HttpResponseRedirect('/accounts/profile/')

        else:
            return render(request, 'change_password.html', {'errors': errors})

    return render(request, 'change_password.html', {'errors': errors})




@login_required(login_url="/accounts/login/")
def change_email(request):
    """
    handles change of email
    :param request: http request
    :return: http request
    """

    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            request.user.email = cd['newEmail']
            request.user.save()
            return HttpResponseRedirect('/accounts/profile/')

    else:
        form = ChangeEmailForm()

    return render(request, 'change_email.html', {'form': form})


@login_required(login_url="/accounts/login/")
def user_change_address(request):
    """
    handles change of address by users
    :param request: http request
    :return: http request
    """
    if request.method == 'POST':
        form = ChangeAddressForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            newAddress = cd['newAddress']

            if request.session['usertype']== 'doctor':
                theUser = Doctor.objects.get(userProfile__user=request.user)
            elif request.session['usertype']=='patient':
                theUser = Patient.objects.get(userProfile__user=request.user)
            elif request.session['usertype']=='nurse':
                theUser = Nurse.objects.get(userProfile__user=request.user)

            theUser.address = newAddress
            theUser.save()
            return HttpResponseRedirect('/accounts/profile/')

    else:
        form = ChangeAddressForm()

    return render(request, 'change_address.html', {'form': form})


@login_required(login_url="/accounts/login/")
def user_change_phoneNo(request):
    """
    handles change of Phone number
    :param request: http request
    :return: http request
    """

    if request.method =='POST':
        form = ChangePhoneNoForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if request.session['usertype']== 'doctor':
                theUser = Doctor.objects.get(userProfile__user=request.user)
                theUser.phoneNo = cd['newPhoneNo']
                theUser.save()
            elif request.session['usertype']=='patient':
                theUser = Patient.objects.get(userProfile__user=request.user)
                theUser.phoneNo = cd['newPhoneNo']
                theUser.save()
            elif request.session['usertype']=='nurse':
                theUser = Nurse.objects.get(userProfile__user=request.user)
                theUser.phoneNo = cd['newPhoneNo']
                theUser.save()
            elif request.session['usertype']== 'pharmacy':
                theUser = Pharmacy.objects.get(userProfile__user=request.user)
                theUser.phoneNo = cd['newPhoneNo']
                theUser.save()

            return HttpResponseRedirect('/accounts/profile/')
    else:
        form = ChangePhoneNoForm()

    return render(request, 'change_phoneNo.html', {'form': form})



@user_passes_test(user_access_history, login_url="/accounts/login/")
def generate_history_report(request, patientId):
    """
    generates report of patients' history
    :param request: http request
    :param patientId: patient Id
    :return: http response
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    thePatient = Patient.objects.get(pk=int(patientId))
    theHistory = PatientHistory( thePatient, request).computeHistory()
    theReport = ReportGenerator(request,theHistory, thePatient.get_name()).report()

    doc = SimpleDocTemplate(response)

    doc.build(theReport)
    return response



def solution(request):
    return render (request, 'solutions.html')


def success(request, event = None,
                        message=None):

    return render(request, 'success.html', {'event': event,
                                          'message': message
                                            })

def userSuccess(request, event):
    return render(request, 'userSuccess.html', {'event': event})

def register(request):
    return render (request, 'register.html')







