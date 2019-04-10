from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, Subject, Board, TutorSubjects
from phonenumber_field.formfields import PhoneNumberField


class NewTutorForm(forms.ModelForm):


	class Meta:
		model = Tutor
		exclude = {'MyUser'}


class NewTutorTimmingForm(forms.Form):
	def save(self):
		pass
	
	# class Meta:
		# model = Timming
		# fields = {'TimeStart', 'TimeEnd'}
		# field_order = ['TimeStart', 'TimeEnd']
		

class NewTutorSubjectForm(forms.ModelForm):


	class Meta:
		model = TutorSubjects
		fields = {'Subject'}
		required = {'Subject'}


class NewUserForm(UserCreationForm):
	
	class Meta:
		model = User
		fields = {'username', 'password1', 'password2', 'email'}
		required = {'username', 'password1', 'password2', 'email'}
	
	def IsEmailPresent(self):
		email = self.cleaned_data.get('email')
		emails = User.objects.filter(email = email).first()
		if emails is None:
			return False
		else:
			return True
		
	def SaveNewUser(self, active):
		newuser = self.save(commit = False)
#		print(dir(newuser))
		newuser.is_active = active
		newuser.save()
		return newuser
	

class NewMyUserForm(forms.ModelForm):
	
	class Meta:
		model = MyUser
		fields = {'Pic'}
		required = {'Pic'}
		
	def SaveNewMyUser(self, person, user, status, type):
		myuser = self.save(commit = False)		
		myuser.user = user
		myuser.PersonID = person
		myuser.Type = type
		myuser.Status = status
		myuser.save()
		return myuser

					 
		
class NewPersonForm(forms.ModelForm):
	CNIC = forms.CharField(required = True)
	FullName = forms.CharField(required = True)
	Phone = PhoneNumberField(required = True)

	class Meta:
		model = Person
		fields = {'CNIC', 
					 'FullName', 'Phone'
				 }	
		required = {'CNIC', 
					 'FullName', 'Phone'
				 }	
				 
	def DoesCnicHaveAccount(self):
		cnic = self.cleaned_data.get('CNIC')
		matching_cnics = MyUser.objects.filter(PersonID__CNIC = cnic).first()
		if matching_cnics is None:
			return False
		else:
			return True

	def SaveNewPerson(self):
		return self.save()

	
class NewBrokerForm(forms.Form):
	def SaveNewBroker(self, myuser):
		cuser = CUser.objects.create(MyUser = myuser, Type = 'Broker')
		return Broker.objects.create(CUser = cuser)


	
class NewStudentForm(forms.Form):
	def SaveNewStudent(self):
		pass



