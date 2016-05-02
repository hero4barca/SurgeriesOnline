from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404, HttpResponseRedirect
from surgeriesOnline.models import *
from surgeriesOnline.forms import *
import  random, string, datetime
from surgeriesOnline.view_dir.views import success
from django.core.mail import send_mail
from surgeriesOnline import tasks

# defines view for action of the Surgery Administrator
#all funtions defined require the user to be looged as a surgery administartor

#used to enforce surgery surgeryAdmin status for all surger surgeryAdmin operations
def user_is_surgeryAdmin( user):
    try:
        userProfile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False
    return user.is_authenticated() and userProfile.usertype =='surgeryAdmin'


def make_transfer(request, transferId):
    """
    makes transfer by changing the surgery associated with a patient
    :param request: http request
    :param transferId: transfer Id
    :return: http response
    """

    theTransfer = PatientTransfer.objects.get(pk=transferId)
    thePatient = theTransfer.patient
    theUserProfile = thePatient.userProfile

    theUserProfile.surgery = theTransfer.toSurgery

    thePatient.surgery = theTransfer.toSurgery

    theTransfer.transferStatus = True
    theTransfer.transferDate = datetime.datetime.now().date()

    theUserProfile.save()
    thePatient.save()
    theTransfer.save()

    return HttpResponseRedirect('/surgeryAdmin/transfer_from_request/')

def accept_patient_transfer_request(request, transferId):
    """
    accepts the trasfer request of a patient to asurgery
    :param request: http request
    :param transferId: transfer Id
    :return: http response
    """

    theTransfer = PatientTransfer.objects.get(pk=transferId)
    theTransfer.approve = True
    theTransfer.approvalDate = datetime.datetime.now().date()
    theTransfer.save()

    return HttpResponseRedirect('/surgeryAdmin/transfer_to_request')



def decline_patient_transfer_request(request, transferId):
    """
    declines the transfer request of a patient to a surgery
    :param request: http request
    :param transferId: transefer id
    :return: http response
    """

    theTransfer = PatientTransfer.objects.get(pk=transferId)
    theTransfer.approve = False
    theTransfer.approvalDate = datetime.datetime.now().date()
    theTransfer.save()

    return HttpResponseRedirect('/surgeryAdmin/transfer_to_request')



def transfer_request_details(request, transferId):
    """
    diplays the details of a transfer request
    :param request: http request
    :param transferId: transfer Id
    :return: http response
    """

    theTransfer = PatientTransfer.objects.get(pk=transferId)
    patientUser = theTransfer.patient.userProfile.user

    return render(request, 'surgeryAdmin/transfer_details.html', {'transfer': theTransfer,
                                                     'requestUser': patientUser})


def patient_transfer_to(request):
    """
    patient display trasnfer request from patient to a surgery
    :param request: http request
    :return: http response
    """

    try:
        transfers = PatientTransfer.objects.filter(toSurgery_id= request.session['surgeryId'])

    except PatientTransfer. DoesNotExist:
        transfers = None

    return render (request, 'surgeryAdmin/patient_transfer_to.html', {'transfer': transfers})


def patient_transfer_from(request):
    """
    displays pateint request to transfer from a surgery
    :param request: http request
    :return: http response
    """

    try:
        transfers = PatientTransfer.objects.filter(fromSurgery_id= request.session['surgeryId'])

    except PatientTransfer. DoesNotExist:
        transfers = None

    return render(request, 'surgeryAdmin/patient_transfer_from.html', {'transfer': transfers})



@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def admin_add_pharm(request):
    """
    adds a pahrmacy to a surgery
    :param request: http request
    :return: http response
    """


    try:
        surgeryPharm = Pharmacy.objects.get(surgery__name= request.session['userSurgery'],
                                            surgery_id=request.session['surgeryId'])
        return success(request,
             message =''' you already added a pharmacy to this surgery, a surgery can only have one pharmacy
                            <a href='/accounts/profile/'> back</a>''')

    except Pharmacy.DoesNotExist:
        surgeryPharm = None

    if request.method == 'POST':
        form = AddPharmacyForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            #generete password
            randomPassword = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(9)])
            randomPassword = 'password'#temp measure
            # update model
             #crete user object

            newPharmUser = User.objects.create_user(username=cd['username'],email=cd['email'],
                                                      password=randomPassword)
            newPharmUser.save()

            #create userProfile
            newPharmProfile = UserProfile(user=newPharmUser, usertype='pharmacy', surgery=Surgery.objects.get(name=request.session['userSurgery']) )
            newPharmProfile.save()

            #create pharmacy object
            newPharmacy = Pharmacy(userProfile=newPharmProfile, surgery=Surgery.objects.get(name=request.session['userSurgery']), deptName=cd['deptName'], phoneNo=cd['phoneNo'])
            newPharmacy.save()

            #  *****Code to send the automically generated password to the user's email here*******
            tasks.send_new_account_mail.delay(newPharmUser.username, newPharmUser.email,
                                              newPharmProfile.usertype, newPharmProfile.surgery.name, randomPassword)

            #redirect for success
            return  HttpResponseRedirect('/add_pharmacy/success/')
    else:
        form = AddPharmacyForm()
    return render (request, 'surgeryAdmin/add_pharmacy.html', {'form': form})



@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def admin_add_clinicalStaff(request, userType):
    """
     allows a surgery surgeryAdmin to add a medical personnel i.e. (Nurse/Doctor) to the surgery
     processes the addPharmacy form and creates the pharmacy
     also creates the User, UserProfile objects
    :param request:
    :param userType:
    :return:
    """
    if request.method == 'POST':
        form = AddMedicalPersonnel(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # update model
             #crete user object

            #generete password
            randomPassword = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(9)])
            randomPassword = 'password'#temp measure

            newUser = User.objects.create_user(username=cd['username'],email=cd['email'],
                                                      password=randomPassword, first_name=cd['firstname'],
                                                 last_name=cd['lastname'])
            newUser.save()

            #create userProfile
            newPersonnelProfile = UserProfile(user=newUser, usertype= userType, surgery=Surgery.objects.get(name=request.session['userSurgery']) )
            newPersonnelProfile.save()

            if userType=='doctor':

                #create doctor
                newDoctor = Doctor(userProfile=newPersonnelProfile, surgery=Surgery.objects.get(name=request.session['userSurgery']),
                                   phoneNo=cd['phoneNo'], staffNo=cd['staffNo'], address=cd['address'])
                newDoctor.save()

                #redirect for success
                tasks.send_new_account_mail.delay(newUser.username, newUser.email,
                                                  newPersonnelProfile.usertype, newPersonnelProfile.surgery.name, randomPassword)
                return  HttpResponseRedirect('/add_doctor/success/')
            else:
                #create nurse
                newNurse = Nurse(userProfile=newPersonnelProfile, surgery=Surgery.objects.get(name=request.session['userSurgery']),
                                   phoneNo=cd['phoneNo'], staffNo=cd['staffNo'], address=cd['address'])
                newNurse.save()

                #  *****Code to send the automically generated password to the user's email here*******

                #redirect for success
                tasks.send_new_account_mail.delay(newUser.username, newUser.email,
                                                  newPersonnelProfile.usertype, newPersonnelProfile.surgery.name, randomPassword)

                return  HttpResponseRedirect('/add_nurse/success/')
    else:
        form = AddMedicalPersonnel()

    if userType == 'doctor':
        templateName ='surgeryAdmin/add_doctor.html'
    else:
        templateName = 'surgeryAdmin/add_nurse.html'

    return render (request, templateName, {'form': form})



@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def admin_add_patient(request):
    """
    # allows a surgery surgeryAdmin to add a patient to the surgery
    # processes the AddPatient Form and creates the Patient
    # also creates the User, UserProfile objects
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = AddPatientForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            #generete password
            randomPassword = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(9)])
            randomPassword = 'password'#temp measure

            currentSurgery = Surgery.objects.get(name=request.session['userSurgery'])
            # update model

            #crete user object
            newPatientUser = User.objects.create_user(username=cd['username'],email=cd['email'],
                                                      password=randomPassword, first_name=cd['firstname'],
                                                      last_name=cd['lastname'])
            newPatientUser.save()

            #create userProfile
            newPatientProfile = UserProfile(user=newPatientUser, usertype='patient', surgery=currentSurgery )
            newPatientProfile.save()

            #create patient object
            newPatient = Patient(userProfile=newPatientProfile, surgery=currentSurgery,address=cd['address'],
                                 phoneNo=cd['phoneNo'], NHS_No=cd['NHSno'])
            newPatient.save()


            tasks.send_new_account_mail.delay(newPatientUser.username, newPatientUser.email,
                                              newPatientProfile.usertype, newPatientProfile.surgery.name, randomPassword)
            #redirect for success
            return  HttpResponseRedirect('/add_patient/success/')
    else:
        form = AddPatientForm()
    return render (request, 'surgeryAdmin/add_patient.html', {'form': form})

@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def show_doctors(request):
    """
    shows a surgeries doctors
    :param request: http request
    :return: http response
    """

    doctors = Doctor.objects.filter(surgery__name= request.session['userSurgery'],
                                    surgery_id= request.session['surgeryId'])

    return render(request, 'surgeryAdmin/show_doctors.html', {'doctors': doctors})


@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def show_nurses(request):
    """
    shows a surgeries nurses
    :param request: http request
    :return: http response
    """
    nurses = Nurse.objects.filter(surgery__name= request.session['userSurgery'],
                                    surgery_id= request.session['surgeryId'])

    return render(request, 'surgeryAdmin/show_nurses.html', {'nurses': nurses})


@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def show_patients(request):
    """
    shows the patients registered with a surgery
    :param request: http request
    :return: http response
    """
    patients = Patient.objects.filter(surgery__name= request.session['userSurgery'],
                                    surgery_id= request.session['surgeryId'])

    return render(request, 'surgeryAdmin/show_patients.html', {'patients': patients})


@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def show_pharmacy(request):
    """
    show a details about a surgeries pahrmacy where there is one
    :param request: http request
    :return: http response
    """
    pharm = Pharmacy.objects.filter(surgery__name= request.session['userSurgery'],
                                    surgery_id= request.session['surgeryId'])

    return render(request, 'surgeryAdmin/show_pharm.html', {'pharm': pharm})


#allows deletion of nurses
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def delete_nurse(request, nurseId):
    """
    delete nurse from a surgery
    :param request: http request
    :param nurseId: nurse Id
    :return: http response
    """

    theNurse = Nurse.objects.get(pk=nurseId)
    theProfile = theNurse.userProfile
    theUser = theProfile.user

    theNurse.delete()
    theProfile.delete()
    theUser.delete()

    return HttpResponseRedirect('/surgeryAdmin/nurses/')

#allows deletion of doctors
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def delete_doctor(request, doctorId):
    """
    deletes a doctor from a surgery
    :param request: http request
    :param doctorId: doctor Id
    :return: http response
    """

    theDoctor = Doctor.objects.get(pk=doctorId)
    theProfile = theDoctor.userProfile
    theUser = theProfile.user

    theDoctor.delete()
    theProfile.delete()
    theUser.delete()

    return HttpResponseRedirect('/surgeryAdmin/doctors/')


@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def delete_patient(request, patientId):
    """
    delete a patient from a surgery
    :param request: http request
    :param patientId: patient Id
    :return: http response
    """
    thePatient = Patient.objects.get(pk=patientId)
    theProfile = thePatient.userProfile
    theUser = theProfile.user

    thePatient.delete()
    theProfile.delete()
    theUser.delete()

    return HttpResponseRedirect('/surgeryAdmin/patients/')

#allows deletion of pharmacy
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def delete_pharmacy(request, pharmId):
    """
    delete a pharmacy from a surgery
    :param request: http request
    :param pharmId: pharmacy Id
    :return: http response
    """

    thePharm = Pharmacy.objects.get(pk=pharmId)
    theProfile = thePharm.userProfile
    theUser = theProfile.user

    thePharm.delete()
    theProfile.delete()
    theUser.delete()

    return HttpResponseRedirect('/surgeryAdmin/pharmacy/')

#allows display of surgery's users
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def show_surgery_users(request):
    """
    display all the users from a surgery
    :param request: http request
    :return: http response
    """

    userProfiles = UserProfile.objects.filter(surgery_id= request.session['surgeryId'])

    return render(request, 'surgeryAdmin/show_user.html', {'profiles': userProfiles})

#allows surgeryAdmin deactivate a user's account
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def deactivate_user(request, userId):
    """
    deactivates a surgery's user
    :param request:http request
    :param userId: user Id
    :return: http respponse
    """
    theUser = User.objects.get(pk=userId)
    theUser.is_active = False
    theUser.save()
    return HttpResponseRedirect('/surgeryAdmin/show_all_users/')

#allows surgeryAdmin to reactivate a users account
@user_passes_test(user_is_surgeryAdmin,login_url="/accounts/login/")
def reactivate_user(request, userId):
    """
    activate a user
    :param request: http request
    :param userId: user Id
    :return: http response
    """
    theUser = User.objects.get(pk=userId)
    theUser.is_active = True
    theUser.save()
    return HttpResponseRedirect('/surgeryAdmin/show_all_users/')

#allows surgeryAdmin to reset a user's password
def reset_user_password(request, userId):
    """
    reset a user's password
    :param request: http request
    :param userId: user Id
    :return: http response
    """
    theUser = User.objects.get(pk=userId)

    randomPassword = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(9)])
    theUser.set_password(randomPassword)

    send_mail('Password reset',
                       'Your new password is: '+ randomPassword +'. /n Your are advised to reset you password on login',
                       'surgeryAdmin@'+ request.session['userSurgery']+'_surgeriesOnline.com',
                    [request.user.email])

    return HttpResponseRedirect('/surgeryAdmin/show_all_users/')



