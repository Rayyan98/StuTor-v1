from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime


# Create your models here.

class Person(models.Model):
	CNIC = models.CharField(max_length = 13, blank = False, null = False)
	FullName = models.CharField(max_length=100, blank = False, null = False)
	Phone = PhoneNumberField(blank = False, null = False, unique = True)

	class Meta:
		verbose_name_plural = "Person"
		
	def __str__(self):
		return self.get_str()
		
	def get_str(self):
		return self.FullName	

	
	
class MyUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank = False, null = False, 						unique = True)
	Pic = models.ImageField()
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



class Tutor(models.Model):
	MyUser = models.OneToOneField(MyUser, on_delete=models.CASCADE, unique = True)
	Qualification = models.OneToOneField(Qualification, on_delete = models.SET_NULL, null = True)
	Degree = models.CharField(max_length = 100)
	Institution = models.CharField(max_length = 100)
	DegreeImage = models.ImageField()

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

