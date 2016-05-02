"""localGps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import *# , url,patterns,include
from django.contrib import admin
from django.contrib.auth.views import login, logout

from surgeriesOnline.view_dir.views import *
from surgeriesOnline.view_dir.medicalPersonnelViews import *
from surgeriesOnline.view_dir.patientViews import *
from surgeriesOnline.view_dir.pharmacyViews import *
from surgeriesOnline.view_dir.surgeryAdminViews import *
from surgeriesOnline.view_dir.specializedFacilityViews import *

from surgeriesOnline.tasks import *

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),#admin site redirect
    url(r'^index/$', index), # dierect index to site homepage
    url(r'^$', index), #url config for site root
    url(r'^solution/$', solution), # redirect to solutions page
    url(r'^register/$', register),#registration page
    url(r'^contact/$', contact),#contact page
    url(r'^project/$', project_details),#contact page

    url(r'^contact_email_sent/$', success, {'event': 'sent your message'}),#success page

    url(r'^register/register_surgery/$', register_surgery), #registering a surgery
    url(r'^register/success/$', success,{'event': 'setup a surgery online portal'}),# redirect after successful registration of a surgery

     url(r'^register/hospital/$', register_specializedFacility), #registering a surgery
    url(r'^register_hospital/success/$', success,{'event': 'registered a hospital'}),# redirect after successful registration of a surgery

    url(r'^register/register_patient/$', register_patient), #registering a
    url(r'^register_patient/success/$', success,{'event': 'registered with your surgery'}),# redirect after successful patient registration

    url(r'^accounts/login/$',  login, {'template_name':'login.html'}),#login, uses django default view
    url(r'^accounts/profile/$', userAccountHome),# redirect to create user sessions after loging

    url(r'^accounts/logout/$', logout,{'next_page': '/logout/'}),#logout, using django default view
    url(r'^logout/$', userAccountLogout),#redirect after logout

    #user accounts setting page link
    url(r'^accounts/my_account/$', my_account),
    url(r'accounts/change_password/$', user_change_password),
    url(r'accounts/change_email/$', change_email),
    url(r'accounts/change_address/$',user_change_address),
    url(r'accounts/change_phoneNo/$', user_change_phoneNo),


    url(r'^admin/pharmacy/$', show_pharmacy),# display information about pharmacy
    url(r'^admin/add_pharmacy/$', admin_add_pharm),#add pharmacy to a surgery
    url(r'^add_pharmacy/success/$', userSuccess,{'event':'added a pharmacy'}),#success after adding pharmacy
    url(r'^admin/delete_pharm/(\d+)/$', delete_pharmacy),

    url(r'^admin/doctors/$', show_doctors),# show all the doctors in a surgery
    url(r'^admin/add_doctor/$', admin_add_clinicalStaff, {'userType': 'doctor'}),#add doctor to a surgery
    url(r'^admin/delete_doctor/(\d+)/$', delete_doctor),
    url(r'^add_doctor/success/$', userSuccess,{'event':'added a doctor'}),#displays success after adding a doctor

    url(r'^admin/nurses/$', show_nurses),# show all the nurses in a surgery
    url(r'^admin/add_nurse/$', admin_add_clinicalStaff, {'userType': 'nurse'}),#add nurse to a surgery
    url(r'^admin/delete_nurse/(\d+)/$', delete_nurse),
    url(r'^add_nurse/success/$', userSuccess,{'event':'added a nurse'}),#displays success after adding a nurse

    url(r'^admin/patients/$', show_patients),# show all the patients in a surgery
    url(r'^admin/add_patient/$', admin_add_patient),#add nurse to a patient
    url(r'^admin/delete_patient/(\d+)/$', delete_patient),
    url(r'^add_patient/success/$', userSuccess,{'event':'added a patient'}),#displays success after adding a patient

    url(r'^admin/show_all_users/$', show_surgery_users),#displays all the user in the surgery
    url(r'^admin/deactivate_user/(\d+)/$', deactivate_user),#sets user.is_active to False
    url(r'^admin/reactivate_user/(\d+)/$', reactivate_user),#sets to true
    url(r'^admin/reset_user_password/(\d+)/$', reset_user_password),

    #url(r'^accounts/mySchedule/$', calendar,{'pYear':2016, 'pMonth':3}),#manage working schedule for medical staff
    url(r'^accounts/mySchedule/$', myScheduleCalendar),
    url(r'^accounts/mySchedule/(\d{4})/(\d{1,2})/$', prevOrNextScheduleCalendar),
    url(r'^accounts/save_schedule/$', save_schedule),
    url(r'^schedule_update/success/$', userSuccess,{'event':'updated you schedule'}),#displays success after updating a medical personnel's schedule
    url(r'^accounts/delete_day_schedule/(\d{4})/(\d{1,2})/(\d{1,2})$', delete_day),


    #***for patients booking doctors appointments and other related functionalities*****
    url(r'^accounts/doctor_appointment/$', show_appointment,{'staffType':'doctor'}),#booking a doctors' appoint index
    url(r'^accounts/doctor_appointment_date/$', show_appointment_date, {'staffType':'doctor'}),
    url(r'^doctor_appointment/book/(\d+)/$', save_appointment, {'staffType':'doctor'}),
    url(r'^accounts/delete_booking/(\d+)/$', delete_booking, {'staffType':'doctor'}),

    #***for patients booking nurse appointments and other related functionalities*****
    url(r'^accounts/nurse_appointment/$', show_appointment,{'staffType':'nurse'}),
    url(r'^accounts/nurse_appointment_date/$', show_appointment_date, {'staffType':'nurse'}),
    url(r'^nurse_appointment/book/(\d+)/$', save_appointment, {'staffType':'nurse'}),
    url(r'^accounts/delete_nurse_booking/(\d+)/$', delete_booking, {'staffType':'nurse'}),

    #***for doctors accessing booked appointments and other related view_dir
    url(r'^doctor_accounts/booked_appointment/$', my_patient_booking, {'staffType':'doctor'}),
    url(r'^doctor_accounts/booked_appointment_date/$', my_patient_booking_date,{'staffType':'doctor'}),

    #***for nurses accessing booked appointments and other related view_dir
    url(r'^nurse_accounts/booked_appointment/$', my_patient_booking, {'staffType':'nurse'}),
    url(r'^nurse_accounts/booked_appointment_date/$', my_patient_booking_date,{'staffType':'nurse'}),

    #for access to patients records during appointments: Doctors
    url(r'^doctor_accounts/appointment_patient_records/(\d+)/$', current_patient_appointment, {'staffType':'doctor'}),#display patient consultation form
    url(r'^doctor_accounts/update_patient_records/$', save_patient_appointment,{'staffType':'doctor'}),#updates patient consultation form

    #urls to consultation forms- for recording appointment details and updating records
    url(r'^nurse_accounts/appointment_patient_records/(\d+)/$', current_patient_appointment,{'staffType':'nurse'}),
    url(r'^nurse_accounts/update_patient_records/$', save_patient_appointment, {'staffType':'nurse'}),

    #urls to closing patient appointment as completed
    url(r'^doctor_accounts/appointment_close/(\d+)/$', close_completed_appointment, {'staffType':'doctor'}),
    url(r'^nurse_accounts/appointment_close/(\d+)/$', close_completed_appointment, {'staffType':'nurse'}),

    #urls for pharmacy accounts operations
    url(r'^accounts/pending_prescriptions/$', pending_prescriptions),
    url(r'^prescription/set_price/(\d+)/$',set_prescription_price),
    url(r'^prescription/save_price/$',save_prescription_price),


    url(r'^accounts/medical_history/$', show_medical_history),#patient access to their medical history
    url(r'^accounts/show_prescriptions/$', show_prescriptions),#patient access to their prescription records
    url(r'^accounts/prescription_payment/(\d+)/$', payment),
    url(r'^successful_payment/$', successful_payment),
    url(r'^accounts/prescription_delivery/(\d+)/$', make_prescription_delivery),

    url(r'^accounts/generate_report/(\d+)/$', generate_history_report),

    url(r'^accounts/referrals/$', show_referrals),#displays all of a patient's referrals
    url(r'^accounts/patient_ref_details/(\d+)/$', my_ref_details),#displays the details of a referral
    url(r'^accounts/accept_ref_date/(\d+)/$',accept_ref_date ),#allows patient to accept a referral date
    url(r'^accounts/reject_ref_date/(\d+)/$', reject_ref_date),#alows patient to reject a referral date



    url(r'^accounts/hospital_referrals/$', hospital_referrals),#displays all the referrals to a particular facility
    url(r'^accounts/scheduled_referrals/$', scheduled_referrals),#displays scheduled referrals
    url(r'^accounts/referral_details/(\d+)/$', referral_details),#displays referral details
    url(r'^accounts/fix_referral_appointment/(\d+)/$', fix_referral),#allows fixing of referrals
    url(r'^accounts/save_referral_time/$', save_ref_appointment), # allows hospital to save referral time
    url(r'^accounts/close_referral/(\d+)/$', close_referral),# closes the referral

    #*****Surgery Transfer*****
    url(r'^accounts/request_surgery_transfer/$', request_transfer),#allows patient to request a surgery transfer
    url(r'^admin/transfer_from_request/$', patient_transfer_from),# allows surgeryAdmin to view request from their surgery
    url(r'^admin/transfer_to_request/$', patient_transfer_to),# allows surgery admin to view request to their surgery
    url(r'^admin/accept_patient_transfer_request/(\d+)/$',accept_patient_transfer_request),# allows the surgery admin to accept a request to his surgery
    url(r'^admin/decline_patient_transfer_request/(\d+)/$',decline_patient_transfer_request),#allows admin to reject a request to his surgery
    url(r'^admin/transfer_request_details/(\d+)/$',transfer_request_details),#allows surgery admin to view transfer details
    url(r'^admin/transfer_patient/(\d+)/$', make_transfer ),#allows the 'from' surgery admin to execute the transfer

    url(r'^doctor_accounts/previous/$', doctor_previous_appointments),
    url(r'^nurse_accounts/previous/$', nurse_previous_appointments),

    url(r'^test_celery/$', test_celery ),
    url(r'^test_notification/$', send_daily_notification ),









]
