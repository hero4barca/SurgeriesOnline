import re, datetime, calendar
from surgeriesOnline.models import *


class MonthScheduleCalendar():

    def __init__(self,request,theDate):
        calendar.setfirstweekday(6)
        self.request = request
        self.givenDate = theDate
        self.monthday = datetime.datetime.date(theDate)
        self.monthList = ['January',  'February',  'March',  'April',  'May',
                 'June',  'July',  'August',  'September',  'October',
                 'November',  'December']

    def split_monthday(self):
        currentSplit = re.split('-', str(self.monthday))
        current_no = int(currentSplit[1])
        monthday_split ={}
        monthday_split['current_monthno']=current_no
        monthday_split['current_monthname'] = self.monthList[current_no-1]
        monthday_split['theday'] = int(re.sub('\A0', '', currentSplit[2]))
        monthday_split['current_yr'] = int(currentSplit[0])

        return monthday_split

    def month(self):
      month = calendar.monthcalendar(self.split_monthday()['current_yr'],self.split_monthday() ['current_monthno'])
      return month


    def noWeeks(self):
        theMonth = self.month()
        return len(theMonth)

    #computes the numeric value previous month
    def previousMonth(self):
        theMonth = self.split_monthday()['current_monthno']
        previousMonth = theMonth-1
        if previousMonth == 0:
            previousMonth = 12
        return previousMonth

    #computes the numeric value of the previous year
    def previousyear(self):
        theMonth = self.split_monthday()['current_monthno']
        theYear = self.split_monthday()['current_yr']
        previousMonth = theMonth-1
        if previousMonth == 0:
            theYear = theYear -1
        return theYear

    #computes the numeric value of the nest month
    def nextMonth(self):
        theMonth = self.split_monthday()['current_monthno']
        nextMonth = theMonth+1
        if nextMonth == 13:
            nextMonth = 1
        return nextMonth

    #computes the numeric value of the next year
    def nextyear(self):
        nextMonth = self.split_monthday()['current_monthno']
        nextYear = self.split_monthday()['current_yr']
        nextMonth = nextMonth+1
        if nextMonth == 13:
            nextYear = nextYear +1
        return nextYear

    #formats the display of a month on the calendar
    def format_display(self):
        theMonth = self.month()

        # check if the processed date is the current date
        thedatesplit = self.split_monthday()
        today = datetime.datetime.date(datetime.datetime.now())
        today_split =  re.split('-', str(today))
        current_month = int(today_split[1])
        current_year = int(today_split[0])
        current_day = int(today_split[2])

        if current_month == int(thedatesplit['current_monthno']) and current_year == int(thedatesplit['current_yr']):
            today_day = current_day
        else:
            today_day = 0


        calStr = '''  <table id="calendar" >  <thead >  <tr >  <th class="weekend" >Sunday</th >
                <th >Monday</th >  <th >Tuesday</th > <th >Wednesday</th >   <th >Thursday</th >  <th >Friday</th >
                  <th class="weekend" >Saturday</th >  </tr >  </thead >  <tbody >  '''

        for weekNo in range(0, len(theMonth)):
            week = theMonth[weekNo]
            calStr = calStr + ''' <tr>'''
            for x in xrange(0,7):
                day = week[x]
                if x == 6 or  x==7:
                    dayType = 'weekend'
                else:
                    dayType = 'day'


                if day == 0:
                    #dayType = 'previous'
                    calStr = calStr + '<td class="previous"></td>'

                    # scheduling knowledge is now relevant
                elif day == today_day:
                    calStr = calStr+ '<td class="%s" id="today"><div > <strong>%s ' %(dayType, day)
                    if not x == 0 and not x == 6:
                        if self.is_booked(day):
                            calStr = calStr + self.booked_day(day)
                        else:
                             calStr = calStr +self.unbooked_day(day)

                    calStr = calStr +'</strong></div></td>'

                else:
                    calStr = calStr+ '<td class="%s"><div >%s' %(dayType, day)
                    if not x == 0 and not x == 6:
                        if today <= datetime.date(year=thedatesplit['current_yr'], month=thedatesplit['current_monthno'], day= day):
                            if self.is_booked(day):
                                #assert False
                                calStr = calStr + self.booked_day(day)
                            else:
                                calStr = calStr +self.unbooked_day(day)

                    calStr = calStr +'</div></td>'

            calStr = calStr + "</tr>"

        calStr = calStr + '</tbody>  </table>'
        return calStr


    #verifies if the user is working on the day,
    def is_booked(self,day):
        request = self.request
        day_date = datetime.date(day=day,
                             month=self.split_monthday() ['current_monthno'] ,
                             year= self.split_monthday() ['current_yr'])

        #if user is a doctor
        if request.session['usertype'] == 'doctor':
            try:
               isBooked = DoctorAvailability.objects.filter(date=day_date,
                                                            doctorId__userProfile__user=request.user)
            except DoctorAvailability.DoesNotExist:
                isBooked = None
        else:
            try:
                isBooked = NurseAvailability.objects.filter(date= day_date,
                                                            nurseId__userProfile__user=request.user)
            except NurseAvailability.DoesNotExist:
                isBooked = None

        if  len(isBooked)< 1:
            #assert False
            return False
        else:

            return True

      # display on the box of a day that has been previously saved
    def booked_day(self,day):
        calStr = '<br/>saved <br/>'
        calStr = calStr +'<a href="/accounts/delete_day_schedule/'+ str(self.split_monthday() ['current_yr']) +'/'
        calStr = calStr + str(self.split_monthday() ['current_monthno']) +'/'
        calStr = calStr +  str(day)+'">cancel </a>'
        return calStr


    #formate for  a day that has no saved schedule
    def unbooked_day(self,day):

        thedatesplit = self.split_monthday()
        today = datetime.datetime.date(datetime.datetime.now())
        current_day =  re.split('-', str(today))
        current_month = int(current_day[1])
        current_year = int(current_day[0])

        if today <= datetime.date(year=thedatesplit['current_yr'], month=thedatesplit['current_monthno'], day= day):
             calStr = '<input type="hidden" name="'+str(day) + '", value="'+ str(day) +'"> '
             calStr = calStr+'<input type="checkbox" name="'+ str(day) +'" value="'+ str(day) + '/' + str(thedatesplit['current_monthno'])+  '/' + str( thedatesplit['current_yr']) + '" checked>'

        else:
            calStr = ''

        return calStr



