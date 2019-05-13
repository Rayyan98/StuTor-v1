import main.models as m
from random import random
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from main.hash import encode
import random
from datetime import datetime
from phonenumber_field.phonenumber import PhoneNumber


class Factory:
	photograph = m.MyUser.objects.filter(user__username = 'student').first().Photograph
	Days = list(m.Day.objects.all())
	Subjects = list(m.Subject.objects.all())
	
	
	def CreatePerson(self, phone):
		cnic = phone * 1000
		fullname = "".join([chr(int(i) + 97) for i in str(phone)])
		#phone = "+92"+str(phone)
		phone = PhoneNumber(country_code = 92, national_number = str(phone), country_code_source = 1)
		a = m.Person.objects.create(CNIC = cnic, FullName = fullname, Phone = phone)
		return a
	
	def CreateUser(self, phone):
		a = "".join([chr(int(i) + 97) for i in str(phone)])
		username = a
		email = a+"@"+a+".com"
		u = m.User.objects.create(username = username, email = email)
		u.set_password('zoltar976')
		u.save()
		return u
		
	def CreateMyUser(self, phone, type):
		p = self.CreatePerson(phone)
		u = self.CreateUser(phone)
		my = m.MyUser.objects.create(user = u, PersonID = p, Type = type, Status = "Go", Photograph = self.photograph)
		return my
		
	def CreateCUser(self, phone, type):
		my = self.CreateMyUser(phone, "CUser")
		cuser = m.CUser.objects.create(MyUser = my, Type = type)
		return cuser
	
	def CreateBroker(self, phone):
		cuser = self.CreateCUser(phone, "Broker")
		broker = m.Broker.objects.create(CUser = cuser)
		return broker
		
	def CreateStudent(self, phone):
		cuser = self.CreateCUser(phone, "Student")
		if random.random() < 0.5:
			p = m.Person.objects.all()
			pind = int((len(p) - 1) * random.random())
			guard = p[pind]
			s = m.Student.objects.create(CUser = cuser, Guardian = guard)
		else:
			s = m.Student.objects.create(CUser = cuser)
		return s
		
	def CreateTutorObj(self, phone):
		myuser = self.CreateMyUser( phone, "Tutor")
		q = m.Qualification.objects.all()
		qind = int((len(q) - 1) * random.random())
		qual = q[qind]
		a = "".join([chr(int(i) + 97) for i in str(phone)])
		lat = random.random() * 0.3 + 24.7
		long = random.random() * 0.8 + 66.6
		latlong = str(lat) + ","+ str(long)
		hash = encode(lat, long, precision = 5)
		t = m.Tutor.objects.create(MyUser = myuser, Highest_Qualification = qual, Degree_Name = a, Institution = a, Degree_Image = self.photograph, location = latlong, hash = hash)
		return t
		
	def CreateTutorSubjects(self, t):
		subs = random.sample(self.Subjects, random.randint(1,3))
		for i in subs:
			m.TutorSubjects.objects.create(Tutor = t, Subject = i)
		
	def CreateTimming(self, t):
		days = random.sample(self.Days, random.randint(1,3))
		for i in days:
			s = random.randint(6, 17)
			ss = str(s).zfill(2)
			e = random.randint(1 , 6 ) + s
			es = str(e).zfill(2)
			ss = datetime.strptime(ss, '%H').time()
			es = datetime.strptime(es, '%H').time()
			m.Timming.objects.create(Tutor = t, Day = i, TimeStart = ss, TimeEnd = es)
		

	def CreateTutor(self, phone):
		t = self.CreateTutorObj(phone)
		self.CreateTutorSubjects(t)
		self.CreateTimming(t)
		return t

		
	def FillDataBase(self, n):
		a = random.sample(range(1000000000, 10000000000), n)
		for i in a:
			x = random.random()
			if x<0.3:
				self.CreateTutor(i)
			elif x>0.95:
				self.CreateBroker(i)	
			else:
				self.CreateStudent(i)
		
		
	
	
	