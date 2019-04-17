from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, Subject, Board, TutorSubjects
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.layout import Field
from bootstrap3_datetime.widgets import DateTimePicker


#---------------------------No idea what is below here --------------------#



#---------------------------Below this we know-----------------------------#	

class NewTutorForm(forms.ModelForm):

	class Meta:
		model = Tutor
		exclude = {'MyUser'}
		
	def SaveNewTutor(self, myuser):
		newtutor = self.save(commit = False)
		newtutor.MyUser = myuser
		newtutor.save()
		return newtutor
		
	def AddTutorSubjectWithID(self, tutor, subject_id):
		sub = Subject.objects.filter(id = subject_id).first()
		return TutorSubjects.objects.create(Tutor = tutor, Subject = sub)

	def AddTutorSubjects(self, tutor, subject_ids):
		for i in subject_ids:
			self.AddTutorSubjectWithID(tutor, i)
		return True

	def AddTutorTimming(self, tutor, dayId, startTime, endTime):
		day = Day.objects.filter(id = dayId).first()
		return Timming.objects.create(Tutor = tutor, Day = day, TimeStart = startTime, TimeEnd = endTime)
		
	def AddTutorTimmings(self, tutor, days, timmings):
		for i in range(len(days)):
			self.AddTutorTimming(tutor, days[i], timmings[2*i], timmings[2*i+1])
		return True
		
		

class NewTutorTimmingForm(forms.Form):
	def save(self):
		pass
	

		

class NewTutorSubjectForm(forms.Form):

	def save(self):
		pass


class NewUserForm(UserCreationForm):
	
	class Meta:
		model = User
		fields = {'email', 'username', 'password1', 'password2'}
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
		newuser.is_active = active
		newuser.save()
		return newuser
	

class NewMyUserForm(forms.ModelForm):
	
	class Meta:
		model = MyUser
		fields = {'Photograph'}
		required = {'Photograph'}
		
	def SaveNewMyUser(self, person, user, status, type):
		myuser = self.save(commit = False)		
		myuser.user = user
		myuser.PersonID = person
		myuser.Type = type
		myuser.Status = status
		myuser.save()
		return myuser

					 
class NewGuardianForm(forms.Form):
	Guardian_CNIC = forms.CharField(required = False)
	Guardian_FullName = forms.CharField(required = False)
	Guardian_Phone = PhoneNumberField(required = False)
				 
	def SaveNewGuardian(self):
		guardian = Person.objects.create()
		guardian.CNIC = self.cleaned_data.get('Guardian_CNIC')
		guardian.Phone = self.cleaned_data.get('Guardian_Phone')
		guardian.FullName = self.cleaned_data.get('Guardian_FullName')
		guardian.save()
		return guardian


		
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

	def DoesNumberHaveAccount(self):
		phone = self.cleaned_data.get('Phone')
		match_phones = MyUser.objects.filter(PersonID__Phone = phone).first()
		if match_phones is None:
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
	def SaveNewAdultStudent(self,  myuser):
		cuser = CUser.objects.create(MyUser = myuser, Type = 'Student')
		return Student.objects.create(CUser = cuser, Guardian = None)

	def SaveNewMinorStudent(self, myuser, guardian):
		cuser = CUser.objects.create(MyUser = myuser, Type = 'Student')
		return Student.objects.create(CUser = cuser, Guardian = guardian)
		

class PasswordChange(forms.Form):
	old_password = forms.CharField(widget = forms.PasswordInput())
	new_password = forms.CharField(widget = forms.PasswordInput())
	confirm_new_password = forms.CharField(widget = forms.PasswordInput())

