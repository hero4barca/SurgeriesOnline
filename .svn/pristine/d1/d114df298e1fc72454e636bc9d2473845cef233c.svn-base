from django import forms
from django.forms.fields import DecimalField
from surgeriesOnline.models import *
from datetime import timedelta
from django.forms.extras.widgets import SelectDateWidget
from datetime import date, datetime
from calendar import monthrange

class SurgeryRegistrationForm(forms.Form):
    """
    Form for registration of a surgery
    """
    surgeryAddress = forms.CharField()
    surgeryName = forms.CharField()
    regNo = forms.CharField()

    adminUsername = forms.CharField()
    adminPassword = forms.CharField(widget= forms.PasswordInput)
    adminFirstname = forms.CharField(required=False)
    adminLastname = forms.CharField(required=False)
    adminEmail = forms.EmailField()
    adminStaffId = forms.CharField()


class PatientRegistrationForm(forms.Form):
    """
    Form for patient registration with a surgery
    """

    surgery = forms.ModelChoiceField(queryset=Surgery.objects.all() )

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.CharField()
    address = forms.CharField(widget=forms.Textarea)
    phoneNo = forms.CharField()
    NHSno = forms.CharField()


class HospitalRegistrationForm(forms.Form):
    """
    Form for registration of hospitals
    """
    address = forms.CharField(widget=forms.Textarea)
    hospitalName = forms.CharField()

    username = forms.CharField()#user login for hospitals not yet implemented
    password = forms.CharField(widget= forms.PasswordInput) # user login for hospitals not ye implemented
    email = forms.EmailField()
    phoneNo = forms.CharField()



class AddPharmacyForm(forms.Form):
    """
    Form for addin a pharmacy to a surgery
    used by susrgery admin
    """
    deptName = forms.CharField()
    phoneNo = forms.CharField()
    email = forms.CharField()
    username = forms.CharField()


class AddMedicalPersonnel(forms.Form):
    """
    Form object for adding a doctor to a surgery
    used by surgery admin
    """

    username = forms.CharField()
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()

    address = forms.CharField(widget=forms.Textarea)
    phoneNo = forms.CharField()
    staffNo = forms.CharField()


class AddPatientForm(forms.Form):
    """
    Form for addding patient to a surger, used by surgery admin
    """
    username = forms.CharField()

    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    address = forms.CharField(widget=forms.Textarea)
    phoneNo = forms.CharField()
    NHSno = forms.CharField()

#Booking appointment
class BookAppointment(forms.Form):
    date= forms.DateField()


class PatientConsultationForm(forms.Form):
    """
    Form for patient consultation
    used by doctors and nurses
    """

    consultationDetails = forms.CharField(widget=forms.Textarea)
    prescription = forms.BooleanField(required=False)
    prescriptionDetails = forms.CharField(widget=forms.Textarea, required=False)
    referral = forms.BooleanField(required=False)
    referralFacilityName =forms.ModelChoiceField(queryset=SpecializedFacility.objects.all(),required=False)
    referralDetails =forms.CharField(widget= forms.Textarea(), required=False)


    def clean(self):
        """
        custom clean function for PatientConsutationForm
        validate prescriptiona and referral details only if the corresponding checkboxes are true
        :return:
        """
        cd = super(PatientConsultationForm,self).clean()
        cd_prescription = cd.get('prescription')
        cd_prescriptionDetails = cd.get('prescriptionDetails')
        cd_referral = cd.get('referral')
        cd_referralFacilityName = cd.get('referralFacilityName')
        cd_referralDetails = cd.get('referralDetails')

        if cd_prescription:
            if  cd_prescriptionDetails == '':
                #assert False
                self.add_error('prescriptionDetails','no prescription details provided')


        if cd_referral:
            if not cd_referralFacilityName:
                self.add_error('referralFacilityName','no hospital chosen for referral')
            if not cd_referralDetails or cd_referralDetails == '':
                self.add_error('referralDetails','no details given for referrals')


class ChangeEmailForm(forms.Form):
    newEmail = forms.EmailField()

class ChangeAddressForm(forms.Form):
    newAddress = forms.CharField(widget=forms.Textarea)

class ChangePhoneNoForm(forms.Form):
    newPhoneNo = forms.CharField()

class ReferralAppointmentForm(forms.Form):
    fixedDate = forms.DateField()
    fixedTime = forms.TimeField()


class CreditCardField(forms.IntegerField):

    def clean(self, value):
        """Check if given CC number is valid and one of the
           card types we accept"""
        if value and not (len(value) == 13 or len(value) == 16):
            raise forms.ValidationError("Please enter in a valid credit card number.")
        return super(CreditCardField, self).clean(value)

class CCExpWidget(forms.MultiWidget):
    """ Widget containing two select boxes for selecting the month and year"""
    def decompress(self, value):
        return [value.month, value.year] if value else [None, None]

    def format_output(self, rendered_widgets):
        html = u' / '.join(rendered_widgets)
        return u'<span style="white-space: nowrap;">%s</span>' % html

class CCExpField(forms.MultiValueField):
    EXP_MONTH = [(x, x) for x in xrange(1, 13)]
    EXP_YEAR = [(x, x) for x in xrange(date.today().year,
                                       date.today().year + 15)]
    default_error_messages = {
        'invalid_month': u'Enter a valid month.',
        'invalid_year': u'Enter a valid year.',
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.ChoiceField(choices=self.EXP_MONTH,
                error_messages={'invalid': errors['invalid_month']}),
            forms.ChoiceField(choices=self.EXP_YEAR,
                error_messages={'invalid': errors['invalid_year']}),
        )
        super(CCExpField, self).__init__(fields, *args, **kwargs)
        self.widget = CCExpWidget(widgets =
            [fields[0].widget, fields[1].widget])

    def clean(self, value):
        exp = super(CCExpField, self).clean(value)
        if date.today() > exp:
            raise forms.ValidationError(
            "The expiration date you entered is in the past.")
        return exp

    def compress(self, data_list):
        if data_list:
            if data_list[1] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_year']
                raise forms.ValidationError(error)
            if data_list[0] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_month']
                raise forms.ValidationError(error)
            year = int(data_list[1])
            month = int(data_list[0])
            # find last day of the month
            day = monthrange(year, month)[1]
            return date(year, month, day)
        return None

class PresPaymentForm(forms.Form):
    """
    Form for making payment for prescriptions
    """

    number = CreditCardField(required=True, label="Card Number")
    expiration = CCExpField(required=True, label="Expiration")
    cvc = forms.IntegerField(required=True, label="CCV Number",
        max_value=9999, widget=forms.TextInput(attrs={'size': '4'}))

    def __init__(self,*args, **kwargs):
         self.request = kwargs.pop('request', None)#retrieve the http request and use it t initialize the request attribute
         super(PresPaymentForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Custom clean method for class
        Calls the super.clean first
        Creates a new payment instance and attempts to charge the card
        If charge fails, raises a validation error on the form containing the message returned by the api
        """
        cleaned = super(PresPaymentForm, self).clean()

        if not self.errors:
            number = self.cleaned_data["number"]
            exp_month = self.cleaned_data["expiration"].month
            exp_year = self.cleaned_data["expiration"].year
            cvc = self.cleaned_data["cvc"]

            payment = Payment()

            #retrive the Id of the prescription object from sessions
            prescriptionId = self.request.session['prescriptionId']

            # charge the card for this particular prescription
            success, instance = payment.charge( number, exp_month,
                                                exp_year, cvc, prescriptionId)

            if not success:
                raise forms.ValidationError("Error: %s" % instance.message)
            else:
                instance.save()

                # payment successful!
                #save payment details to db only after enesuring that it is successful
                payment.save()

                pass

        return cleaned


class TransferRequestForm(forms.Form):
    """
    Forms for patient surgery transfer request
    """
    toSurgery = forms.ModelChoiceField(queryset=Surgery.objects.all())

    def __init__(self,*args, **kwargs):
         self.request = kwargs.pop('request', None)#initilizes request var with http request object
         super(TransferRequestForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        the clean method compares the transfers surgery and the current
        surgery to ensure that the selected choices are valid
        """

        cleaned = super(TransferRequestForm, self).clean()
        if not self.errors:
            toSurgery = self.cleaned_data['toSurgery']

            if self.request.session['surgeryId'] == toSurgery.pk:

                errMsg = "The transfer surgery can't be your current surgery"
                raise forms.ValidationError("Error: %s" % errMsg)
            else:
                pass

        return cleaned


class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)
















