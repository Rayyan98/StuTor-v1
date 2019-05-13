from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime, date
from location_field.models.plain import PlainLocationField
from django.db.models import Max, Count, Avg

# Create your models here.

class Messages(models.Model):
	sendingUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "user_sent_messages")
	receivingUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "user_received_messages")
	message = models.CharField(max_length = 1000)
	datetime = models.DateTimeField(default = datetime.now)
	status = models.CharField(max_length = 100)
	conversation = models.CharField(max_length = 100)
	
	def CreateNewMessage(sendingUser, receivingUser, message):
		sendingUser = User.objects.filter(username = sendingUser)[0]
		receivingUser = User.objects.filter(username = receivingUser)[0]
		if sendingUser is None or receivingUser is None or message == "":
			pass
		else:
			return Messages.objects.create(sendingUser = sendingUser, receivingUser = receivingUser, message = message,  status = "Pending_View", conversation = str(min(sendingUser.id, receivingUser.id)) + "_" + str(max(sendingUser.id, receivingUser.id)))

	def Get_Last_N_Messages(sendingUser, receivingUser, n):
		unviewed = Messages.objects.filter(sendingUser__username = receivingUser, receivingUser__username = sendingUser, status = "Pending_View")
		finalset = Messages.objects.filter(sendingUser__username = sendingUser, receivingUser__username = receivingUser).order_by('-datetime') | Messages.objects.filter(receivingUser__username = sendingUser, sendingUser__username = receivingUser).order_by('-datetime')
		if len(finalset) < n or len(unviewed) < 1 or unviewed.earliest('datetime').datetime > finalset[n-1].datetime:
			returnSet = finalset[0:n][::-1]
		else:
			returnSet = Messages.objects.filter(id__gte = unviewed.earliest('datetime').id, sendingUser__username = sendingUser, receivingUser__username = receivingUser).order_by('-datetime') | Messages.objects.filter(id__gte = unviewed.earliest('datetime').id, receivingUser__username = sendingUser, sendingUser__username = receivingUser).order_by('-datetime')
			returnSet= returnSet[::-1]
		return returnSet
		
	def get_list_of_users(username, all = False):
		m = Messages.objects.filter(sendingUser__username = username) | Messages.objects.filter(receivingUser__username = username)
		print(dir(m))
		m = m.values('conversation').annotate(date = Max('datetime'), r_username = Max('receivingUser__username'), s_username = Max('sendingUser__username'), unread = Max('status'))
		return m



class Person(models.Model):
	CNIC = models.IntegerField(blank = False, null = False)
	FullName = models.CharField(max_length=100, blank = False, null = False)
	Phone = PhoneNumberField(blank = False, null = False)

	class Meta:
		verbose_name_plural = "Person"
		
	def __str__(self):
		return self.get_str()
		
	def get_str(self):
		return self.FullName	

	
	
class MyUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank = False, null = False, 						unique = True)
	Photograph = models.ImageField()
	Type = models.CharField(max_length=100)
	PersonID = models.OneToOneField(Person, on_delete=models.CASCADE, null = True, unique = True)
	Status = models.CharField(max_length = 50, blank= False, null = False)
	
	class Meta:
		verbose_name_plural = "My Users"
	
	def __str__(self):
		return self.get_str()
		
	def get_str(self):
		return self.PersonID.get_str()
		
	
	
class CUser(models.Model):
	Type = models.CharField(max_length = 100)
	MyUser = models.OneToOneField(MyUser, on_delete=models.CASCADE, unique = True)

	class Meta:
		verbose_name_plural = "Customer Users"
	
	def __str__(self):
		return self.get_str()
	
	def get_str(self):
		return self.MyUser.get_str()

	
class Broker(models.Model):
	CUser = models.OneToOneField(CUser, on_delete=models.CASCADE, unique = True)
	
	def __str__(self):
		return self.get_str()
	
	def get_str(self):
		return self.CUser.get_str()


class Student(models.Model):
	Guardian = models.ForeignKey(Person, on_delete=models.CASCADE, blank = True, null = True)
	CUser = models.OneToOneField(CUser, on_delete=models.CASCADE, unique = True)
	
	def __str__(self):
		return self.get_str()
	
	def get_str(self):
		return self.CUser.get_str()

	
class Day(models.Model):
	Name = models.CharField(max_length=100)

	def __str__(self):
		return self.Name	

	
	
class Qualification(models.Model):
	Name = models.CharField(max_length=100)

	def __str__(self):
		return self.Name

	
	
class Board(models.Model):
	Name = models.CharField(max_length=100)

	def __str__(self):
		return self.Name

		

class Subject(models.Model):
	Board = models.ForeignKey(Board, blank = False, null = False, on_delete = models.CASCADE, 							default = 10)
	Name = models.CharField(max_length=100)
	
	def __str__(self):
		return self.Name + " " + self.Board.Name

	def get_board_and_name(self):
		return self.Board.Name + " " + self.Name


class Tutor(models.Model):
	MyUser = models.OneToOneField(MyUser, on_delete=models.CASCADE, unique = True)
	Highest_Qualification = models.ForeignKey(Qualification, on_delete = models.SET_NULL, null = True)
	Degree_Name = models.CharField(max_length = 100)
	Institution = models.CharField(max_length = 100)
	Degree_Image = models.ImageField()
	location = PlainLocationField(zoom=7)
	hash = models.CharField(max_length = 100)
	
	def __str__(self):
		return self.get_str()

	def get_str(self):
		return self.MyUser.get_str()
		
	def timming_match(self, times):
		days = times[0]
		t = times[1]
		hours = 0
		for i in range(len(days)):
			sd = self.timming_set.filter(Day = days[i])
			if len(sd) == 1:
				dateTimeA = datetime.combine(date.today(), sd[0].TimeEnd)
				dateTimeB = datetime.combine(date.today(), sd[0].TimeStart)
				dateTimeDifference = dateTimeA - dateTimeB
		
				dateTimeA2 = datetime.combine(date.today(), t[2*i + 1])
				dateTimeB2 = datetime.combine(date.today(), t[2*i])
				dateTimeDifference2 = dateTimeA2 - dateTimeB2

				minstart = min(sd[0].TimeStart, t[2*i])
				maxstart = max(sd[0].TimeEnd, t[2*i+1])
				
				dateTimeA3 = datetime.combine(date.today(), maxstart)
				dateTimeB3 = datetime.combine(date.today(), minstart)
				dateTimeDifference3 = dateTimeA3 - dateTimeB3
				
				if dateTimeDifference + dateTimeDifference2 > dateTimeDifference3:
					hours += (dateTimeDifference + dateTimeDifference2 - dateTimeDifference3).total_seconds() / 3600
					if hours >= 4:
						return True
		return False
		
	def get_matching_tutors(hash, subject, times):
		t = Tutor.objects.filter(hash = hash)
		print(len(t), hash)
		l = []
		for i in t:
			if len(i.tutorsubjects_set.filter(Subject = subject)) == 1 and i.timming_match(times):
				l.append(i)
		print(len(l))
		return l
				
	def get_average_rating(self, tutor):
		tutor.contracts_set.

	
class TutorSubjects(models.Model):
	Tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE)
	Subject = models.ForeignKey(Subject, on_delete = models.CASCADE)

	def __str__(self):
		return self.Tutor.get_str()

	

	
class Timming(models.Model):
	Tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE)
	Day = models.ForeignKey(Day, on_delete = models.CASCADE)
	TimeStart = models.TimeField()
	TimeEnd = models.TimeField()
	
	def __str__(self):
		return self.Tutor.get_str()

	
#----------------------------------------------------------------#

class Contracts(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete = models.CASCADE, null= False, blank = False)
	student = models.ForeignKey(Student, on_delete = models.CASCADE, null= False, blank = False)
	subject = models.ForeignKey(Subject, on_delete = models.CASCADE, null= False, blank = False)
	startDate = models.DateTimeField(null= False, blank = False)
	endDate = models.DateTimeField(null= False, blank = False)
	status = models.CharField(max_length = 100)
	review = models.TextField(null = True, blank = True)
	userRating = models.IntegerField(null= True, blank = True)
	tutorRating = models.IntegerField(null = True, blank = True)
	
	
class ContractsTimes(models.Model):
	contract = models.ForeignKey(Contracts, null= False, blank = False, on_delete = models.CASCADE)
	day = models.ForeignKey(Day, null= False, blank = False, on_delete = models.CASCADE)
	timeStart = models.TimeField()
	timeEnd = models.TimeField()
	
	
	
	