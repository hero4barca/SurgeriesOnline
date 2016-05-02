from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from  localGPsProject import settings

# Create your models here.
import datetime

#for encrypting text fields in the database
from fernet_fields import EncryptedTextField

# First, define the Manager subclass.



class Surgery(models.Model):
    '''
    Surgery
    creates and manipulates a surgery object
    '''
    address = models.CharField(max_length= 50)
    name = models.CharField(max_length= 50)
    regNo = models.CharField(max_length= 20)

    def __str__(self):
        return self.name


class Surgery_Specific(models.Manager):
    def get_query_set(self, currentSurgery):
        return super(Surgery_Specific, self).get_query_set().filter(surgery=currentSurgery)

class UserProfile(models.Model):
    '''
    UserProfile
    creates and manipulates a surgery user profile
    '''
    usertype = models.CharField(max_length=15, choices=(('surgeryAdmin', 'surgeryAdmin'), ('doctor', 'doctor'), ('nurse', 'nurse'),
                                                        ('patient', 'patient'), ('pharmacy', 'pharmacy')))
    surgery = models.ForeignKey(Surgery)
    user = models.ForeignKey(User)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s' % (self.user.username, self.usertype)

    def firstname(self):
        return self.user.first_name

    def lastname(self):
        return self.user.last_name

    def fullname(self):
        return '%s  %s' % (self.firstname(), self.lastname())

    def get_email(self):
        return '%s ' % (self.user.email)

    def get_username(self):
        return '%s' % (self.user.username)


class SurgeryAdmin(models.Model):
    '''
    SugeryAdmin
    creates and manipulates the surgery surgeryAdmin user object
    '''
    staffId = models.CharField(max_length=20)
    userProfile = models.ForeignKey(UserProfile)
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s' % (self.userProfile.__str__(), self.staffNo)

class Patient(models.Model):
    '''
    Patient
    creates and manipulates the patient user object
    '''
    address = models.CharField(max_length= 50)
    phoneNo = models.CharField(max_length= 20)
    NHS_No = models.CharField(max_length= 20)
    userProfile = models.ForeignKey(UserProfile)

    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s %s' % (self.userProfile.firstname(), self.userProfile.lastname(), self.NHS_No)

    def get_name(self):
        return '%s %s' % (self.userProfile.firstname(), self.userProfile.lastname())

class Doctor(models.Model):
    '''
    Doctor
    creates and manipulates the Doctors objects
    '''
    address = models.CharField(max_length= 50)
    phoneNo = models.CharField(max_length= 20)
    staffNo = models.CharField(max_length=20)
    userProfile = models.ForeignKey(UserProfile)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s %s' % (self.userProfile.firstname(), self.userProfile.lastname(), self.staffNo)

    def doctor_name(self):
        return '%s %s ' % (self.userProfile.firstname(), self.userProfile.lastname())


class Nurse(models.Model):
    '''
    Nurse
    creates and manipulates the nurse object
    '''
    address = models.CharField(max_length= 50)
    phoneNo = models.CharField(max_length= 20)
    staffNo = models.CharField(max_length=20)
    userProfile = models.ForeignKey(UserProfile)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()
    objects = models.Manager()

    def __str__(self):
        return '%s %s %s' % (self.userProfile.firstname(), self.userProfile.lastname(), self.staffNo)

    def nurse_name(self):
        return '%s %s ' % (self.userProfile.firstname(), self.userProfile.lastname())

class Pharmacy(models.Model):
    '''
    Pharmacy
    creates and manipulate a pharmacy instance
    '''
    userProfile = models.ForeignKey(UserProfile)
    phoneNo = models.CharField(max_length=20)
    deptName = models.CharField(max_length=50)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()
    objects = models.Manager()

    def __str__(self):
        return self.deptName

class DoctorAvailability(models.Model):
    '''
    DoctorAvailability
    cretaes and manipulates the schedule of a doctor
    '''
    doctorId = models.ForeignKey(Doctor)
    timeSlot = models.TimeField()
    date = models.DateField()
    day = models.CharField(max_length=20, blank=True)
    #support multi- tenency
    booked = models.BooleanField(default=False)
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()
    objects = models.Manager()

    def __str__(self):
        return '%s %s %s' % (self.doctorId.__str__(), self.date.__str__(), self.timeSlot.__str__())

    def get_doctor_name(self):
        return self.doctorId.doctor_name()


    def pk_val(self, meta=None):
        return self.pk

    def get_timeslot(self):
        return self.timeSlot



class NurseAvailability(models.Model):
    '''
    NurseAvailabiity
    creates and manipulates the schedule of a nurse
    '''
    nurseId = models.ForeignKey(Nurse)
    timeSlot = models.TimeField()
    date = models.DateField()
    day = models.CharField(max_length=20, blank=True)
    booked = models.BooleanField(default=False)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s %s' % (self.nurseId.__str__(),self.date.__str__(), self.timeSlot.__str__())

    def get_nurse_name(self):
        return self.nurseId.nurse_name()

    def pk_val(self, meta=None):
        return self.pk

    def get_timeslot(self):
        return self.timeSlot

class DoctorBooking(models.Model):
    '''
    Doctor booking
    creates and manipulate a bookings for doctors
    '''
    doctorAvailability = models.ForeignKey(DoctorAvailability)
    patient = models.ForeignKey(Patient)
    status = models.IntegerField(default=0)

    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s' % (self.patient.__str__(), self.doctorAvailability.__str__())

    def pk_val(self, meta=None):
        return self.pk

    def get_patient_name(self):
        thePatient = self.patient
        return thePatient.get_name()

    def get_date(self):
        return self.doctorAvailability.date




class NurseBooking(models.Model):
    '''
    Nurse booking
    creates and maniputes a booking for a nurse
    '''
    nurseAvailability = models.ForeignKey(NurseAvailability)
    patient = models.ForeignKey(Patient)
    status=models.IntegerField(default=0)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return '%s %s' % (self.patient.__str__(), self.nurseAvailability.__str__())

    def pk_val(self, meta=None):
        return self.pk

    def get_patient_name(self):
        thePatient = self.patient
        return thePatient.get_name()

    def get_date(self):
        return self.nurseAvailability.date


class DoctorAppointment(models.Model):
    '''
    Doctor appointment
    creates and manipulates a doctor appointment
    '''

    doctorBooking = models.ForeignKey(DoctorBooking)
    details = EncryptedTextField()
    surgery = models.ForeignKey(Surgery)
    objects = models.Manager()
    surgery_specific = Surgery_Specific()

    def __str__(self):
        return 'appointment for : %s' % (self.doctorBooking.__str__())

    def pk_val(self, meta=None):
        return self.pk

    def get_date(self):
        return self.doctorBooking.get_date()

    def get_patient(self):
        return  self.doctorBooking.get_patient_name()

    def get_doctor(self):
        theBooking = self.doctorBooking
        theAvaibility = theBooking.doctorAvailability

        return theAvaibility.get_doctor_name()




class NurseAppointment(models.Model):
    '''
    Nurse Appointmet
    creates and manipulates a nurse appointment
    '''
    nurseBooking = models.ForeignKey(NurseBooking)
    details = models.TextField()
    surgery = models.ForeignKey(Surgery)
    objects = models.Manager()
    surgery_specific = Surgery_Specific()

    def __str__(self):
        return 'appointment for : %s' % (self.nurseBooking.__str__())

    def pk_val(self, meta=None):
        return self.pk

    def get_date(self):
        return self.nurseBooking.get_date()

    def get_patient(self):
        return  self.nurseBooking.get_patient_name()

    def get_nurse(self):
        theBooking = self.nurseBooking
        theAvaibility = theBooking.nurseAvailability
        return theAvaibility.get_nurse_name()




class Prescription(models.Model):
    '''
    Prescription
    creates and manipulates a prescription object
    '''
    doctorAppointment = models.ForeignKey(DoctorAppointment)
    details = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deliveryStatus = models.BooleanField()
    paymentStatus = models.BooleanField()
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()#support multi- tenency
    objects = models.Manager()

    def __str__(self):
        return self.details.__str__()

    def pk_val(self, meta=None):
        return self.pk

class SpecializedFacility(models.Model):
    '''
    Specialized Facility
    created and manipulates referral facility instances
    '''
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phoneNo = models.CharField(max_length=20)
    objects = models.Manager()


    def __str__(self):
        return self.name



class Referral(models.Model):
    '''
    Referral class
    creates and manipulates referral objects
    '''
    doctorAppointment = models.ForeignKey(DoctorAppointment)
    specializedFacility = models.ForeignKey(SpecializedFacility)
    details = models.TextField()
    status = models.BooleanField(default=False)
    fixedDate = models.DateField(null=True)
    fixedTime = models.TimeField(null=True)
    fixed = models.BooleanField(default=False)
    #support multi- tenency
    surgery = models.ForeignKey(Surgery)
    surgery_specific = Surgery_Specific()
    objects = models.Manager()

    def __str__(self):
        return self.details.__str__()



class Payment(models.Model):
    '''
    Class for payment - implemented using Stripe
    @init  initializes  the payment
    @charge charges the card
    '''
    def __init__(self, *args, **kwargs):
        super(Payment, self).__init__(*args, **kwargs)

        # bring in stripe, and get the api key from settings.py
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY

        self.stripe = stripe

    charge_id = models.CharField(max_length=32)# store the stripe charge id for this payment
    charge_date = models.DateTimeField()#date of the payment
    prescription = models.ForeignKey(Prescription)
    surgery = models.ForeignKey(Surgery)


    def charge(self,  number, exp_month, exp_year, cvc , pres_Id):
        """

        :param number:  card number
        :param exp_month: expiration month
        :param exp_year: expiration year
        :param cvc:  card cvc number
        :param pres_Id: prescription Id
        :return: (Boolean,Class) - if successful (True,Class);(False,error)
        """

        if self.charge_id: #check if card has already been charged
            return False, Exception(message="Already charged for this prescription")

        thePrescription = Prescription.objects.get(pk=pres_Id)
        price_in_cents = int(thePrescription.price * 100)

        try:
            response = self.stripe.Charge.create(
                amount = price_in_cents,
                currency = "usd",
                card = {
                    "number" : number,
                    "exp_month" : exp_month,
                    "exp_year" : exp_year,
                    "cvc" : cvc,

                },
                description='Payment for prescription: surgeriesOnline!')

            self.charge_id = response.id
            self.charge_date = datetime.datetime.now()

            thePrescription.paymentStatus = True
            thePrescription.save()

            self.prescription = thePrescription
            self.surgery = self.prescription.surgery

        except self.stripe.CardError, ce:
            # charge failed
            return False, ce

        return True, response



class PatientTransfer(models.Model):

    """
    Patient Transfer
    Instantiates and manipulates patients transfer form one surgery to another
    """
    patient = models.ForeignKey(Patient)
    fromSurgery = models.ForeignKey(Surgery, related_name='from_surgery')
    toSurgery = models.ForeignKey(Surgery, related_name='to_surgery')
    requestDate = models.DateField()
    transferStatus = models.BooleanField(default=False)
    approvalDate = models.DateField(null=True)#
    approve = models.NullBooleanField()#flags if request has been approved by the to surgery
    transferDate = models.DateField(null=True)
