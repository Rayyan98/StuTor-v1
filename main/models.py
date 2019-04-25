from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime


# Create your models here.

class Messages(models.Model):
	sendingUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "user_sent_messages")
	receivingUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "user_received_messages")
	message = models.CharField(max_length = 100)
	datetime = models.DateTimeField(default = datetime.now)
	


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

	def __str__(self):
		return self.get_str()

	def get_str(self):
		return self.MyUser.get_str()

	
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
	cuser = models.ForeignKey(CUser, on_delete = models.CASCADE, null= False, blank = False)
	subject = models.ForeignKey(Subject, on_delete = models.CASCADE, null= False, blank = False)
	startDate = models.DateTimeField(null= False, blank = False)
	endDate = models.DateTimeField(null= False, blank = False)
	status = models.CharField(max_length = 100)
	review = models.TextField()
	userRating = models.IntegerField()
	tutorRating = models.IntegerField()
	
	
class ContractsTimes(models.Model):
	contract = models.ForeignKey(Contracts, null= False, blank = False, on_delete = models.CASCADE)
	day = models.ForeignKey(Day, null= False, blank = False, on_delete = models.CASCADE)
	timeStart = models.TimeField()
	timeEnd = models.TimeField()
	
	
	
	