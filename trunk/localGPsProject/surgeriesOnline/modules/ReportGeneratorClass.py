import reportlab, StringIO

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


class ReportGenerator():

    def __init__(self, request, theHistory, theName):
        self.history = theHistory
        self.request = request
        self.patientname = theName


    def report(self):

        #define paragraph styles
        style = ParagraphStyle(
                                name='Normal',
                                fontName='Helvetica',
                                fontSize=10 )

        lastLinestyle = ParagraphStyle(
                                name='Normal',
                                fontName='Helvetica',
                                fontSize=7 )

        styles = getSampleStyleSheet()

        reportText = []

        surgeryname = Paragraph('Current Surgery :'+ self.request.session['userSurgery'], styles['Heading3'])

        reportText.append(surgeryname)


        patientLine = Paragraph(" Patient name :" + self.patientname, styles['Heading4'])
        reportText.append(patientLine)
        reportText.append(Spacer(1, 0.15 * inch))

        for record in self.history:
            surgerLine = Paragraph(  str(record['surgery']) , style)
            dateLine = Paragraph("Date:" + str(record['date']) , style)

            if record['type'] == "doctor's":
                typeStr = 'Doctor'
            else:
                typeStr = 'Nurse'

            appointment = 'Appointment with ' + typeStr + ' '+str(record['personnel'])
            appointmentLine = Paragraph(appointment, style)

            notes = typeStr + "'s notes: " + record['appointment'].details
            notesLines = Paragraph(notes,style)

            reportText.append(surgerLine)
            reportText.append(dateLine)
            reportText.append(appointmentLine)
            reportText.append(notesLines)

            if not record['prescription'] == None:

                prescription = 'Prescription: ' + str(record['prescription'].details)
                prescriptionLine = Paragraph(prescription, style)
                reportText.append(prescriptionLine)

            if not record['referral']==None:
                referral = 'Referral: ' + str(record['referral'].details)
                referralLine = Paragraph(referral, style)
                reportText.append(referralLine)

            reportText.append(Spacer(1, 0.15 * inch))

        lastLine = 'This report is automatically generated - SurgeriesOnline'
        lastParagraph = Paragraph(lastLine, lastLinestyle)
        reportText.append(lastParagraph)

        return reportText








