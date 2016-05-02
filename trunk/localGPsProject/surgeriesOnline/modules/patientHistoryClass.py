from surgeriesOnline.models import *
from operator import itemgetter


class PatientHistory():

    def __init__(self, thePatient, request):
        self.patient = thePatient
        self.request = request

    def patient_name(self):
        return self.patient.get_name()

    def patient_pk(self):
        return self.patient_pk()

    def computeHistory(self):

        currentSurgery = Surgery.objects.get(name= self.request.session['userSurgery'])

        #retrieves the appointments form the database
        try:
            docAppointment = DoctorAppointment.objects.filter( doctorBooking__patient = self.patient  )

        except DoctorAvailability.DoesNotExist:
            docAppointment = None

        try:
            nurseAppointment = NurseAppointment.objects.filter( nurseBooking__patient=self.patient  )

        except NurseAvailability.DoesNotExist:
            nurseAppointment = None

        #call the appointment histroy methods to fromat the data
        myDocAppointmentHistoryList = self.docAppointmentsHistory(docAppointment)
        myNurAppointmentHistoryList = self.nurseAppointmentHistory(nurseAppointment)

        #combines the nurse appointment and doctor appointments
        myAppointHistoryList = myDocAppointmentHistoryList + myNurAppointmentHistoryList

        #sort both appointments by date
        historyByDate = sorted(myAppointHistoryList, key=itemgetter('date'))
        return historyByDate



    def docAppointmentsHistory(self,docAppointments):

        myDocAppointmentsHistory =[]

        for appointment in docAppointments:
            appointmentDetails = {}
            appointmentDetails['surgery'] = appointment.surgery.name
            appointmentDetails['type'] = "doctor's"
            appointmentDetails['personnel']=appointment.get_doctor()
            theBooking = appointment.doctorBooking
            appointmentDetails['date'] = theBooking.get_date()
            appointmentDetails['appointment'] = appointment

            try:
                appointmentDetails['prescription'] = Prescription.objects.get(doctorAppointment=appointment)
            except Prescription.DoesNotExist:
                appointmentDetails['prescription'] = None

            try:
                appointmentDetails['referral'] = Referral.objects.get(doctorAppointment=appointment)
            except Referral.DoesNotExist:
                appointmentDetails['referral'] = None

            myDocAppointmentsHistory.append(appointmentDetails)

        return myDocAppointmentsHistory


    def nurseAppointmentHistory(self, nurseAppointments):

        myNurseappointmentsHistory =[]

        for appointment in nurseAppointments:
            appointmentDetails = {}
            appointmentDetails['type'] = "nurse's"
            appointmentDetails['surgery'] = appointment.surgery.name
            appointmentDetails['personnel'] = appointment.get_nurse()
            theBooking = appointment.nurseBooking
            appointmentDetails['date'] =theBooking.get_date()
            appointmentDetails['appointment'] = appointment
            myNurseappointmentsHistory.append(appointmentDetails)

        return myNurseappointmentsHistory


