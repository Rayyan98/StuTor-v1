from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, Subject, Board, TutorSubjects
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.layout import Field
from bootstrap3_datetime.widgets import DateTimePicker
from django.contrib import messages


#---------------------------No idea what is below here --------------------#

#---------------------------Account view and edit forms below here---------#	

class ViewUserForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = {'username', 'email'}
	
	def Freeze(self):
		self.fields.get('username').disabled = True
		self.fields.get('email').disabled = True

	def FreezePartial(self):
		self.fields.get('username').disabled = True		

	def IsEmailPresent(self, user):
		email = self.cleaned_data.get('email')
		emails = User.objects.filter(email = email).first()
		print(emails)
		print(user)
		if emails is None or  emails == user:
			return False
		else:
			return True

	def Validate(self, user):
		return not self.IsEmailPresent(user)

	def Update(self, user):
		user.email = self.cleaned_data.get('email')
		user.save()
		

class PasswordChange(forms.Form):
	old_password = forms.CharField(widget = forms.PasswordInput())
	new_password = forms.CharField(widget = forms.PasswordInput())
	confirm_new_password = forms.CharField(widget = forms.PasswordInput())


#---------------------------Registrations form below here------------------#	


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
		
	def Freeze(self):
		self.fields.get('Highest_Qualification').disabled = True
		self.fields.get('Degree_Name').disabled = True
		self.fields.get('Institution').disabled = True
		self.fields.get('Degree_Image').disabled = True
				
	def UpdatePartial(self, user, save = True):
		user.myuser.tutor.Highest_Qualification = self.cleaned_data.get('Highest_Qualification')
		user.myuser.tutor.Degree_Name = self.cleaned_data.get('Degree_Name')
		user.myuser.tutor.Institution = self.cleaned_data.get('Institution')
		if save:
			user.myuser.tutor.save()
				
	def UpdateFull(self, user):
		self.UpdatePartial(user, False)
		user.myuser.tutor.Degree_Image = self.cleaned_data.get('Degree_Image')
		user.myuser.tutor.save()
		
	def AddTutorTimmingsAdditional(self, user, days, timmings):
		self.AddTutorTimmings(user.myuser.tutor, days, timmings)
		
	def AddTutorSubjectsAdditional(self, user, subject_ids):
		self.AddTutorSubjects(user.myuser.tutor, subject_ids)
		
	def AddTutorTimmingsOverwrite(self, user, days, timmings):
		Timming.objects.filter(Tutor = user.myuser.tutor).delete()
		self.AddTutorTimmings(user.myuser.tutor, days, timmings)
		
	def AddTutorSubjectsOverwrite(self, user, subject_ids):
		TutorSubjects.objects.filter(Tutor = user.myuser.tutor).delete()
		self.AddTutorSubjects(user.myuser.tutor, subject_ids)



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

	def Freeze(self):
		self.fields.get('Photograph').disabled = True

	def Update(self, user):
		user.myuser.Photograph = self.cleaned_data.get('Photograph')
		user.myuser.save()

	def UpdateUserStatus(self, user, status):
		user.myuser.Status = status
		user.myuser.save()


					 
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

	def Freeze(self):
		self.fields.get('Guardian_CNIC').disabled = True
		self.fields.get('Guardian_FullName').disabled = True
		self.fields.get('Guardian_Phone').disabled = True

	def FillInstance(self, guardian):
		self.initial = {'Guardian_CNIC' : guardian.CNIC, 'Guardian_FullName': guardian.FullName, 'Guardian_Phone': guardian.Phone}

	def Update(self, user):
		user.myuser.cuser.student.Guardian.CNIC = self.cleaned_data.get('Guardian_CNIC')
		user.myuser.cuser.student.Guardian.FullName = self.cleaned_data.get('Guardian_FullName')
		user.myuser.cuser.student.Guardian.Phone = self.cleaned_data.get('Guardian_Phone')
		user.myuser.cuser.student.Guardian.save()

		
class NewPersonForm(forms.ModelForm):
	CNIC = forms.IntegerField(required = True)
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
			if len(str(cnic)) != 13:
				return True
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

	def Freeze(self):
		self.fields.get('CNIC').disabled = True	
		self.fields.get('FullName').disabled = True
		self.fields.get('Phone').disabled = True

	def CheckOtherCNIC(self, user):
		cnic = self.cleaned_data.get('CNIC')
		matching_cnics = MyUser.objects.filter(PersonID__CNIC = cnic).exclude(user = user).first()
		if matching_cnics is None:
			if len(str(cnic)) != 13:
				return True
			return False
		else:
			return True

	def CheckOtherPhone(self, user):
		phone = self.cleaned_data.get('Phone')
		match_phones = MyUser.objects.filter(PersonID__Phone = phone).exclude(user = user).first()
		if match_phones is None:
			return False
		else:
			return True

	def Validate(self, user):
		if self.CheckOtherCNIC(user):
			return False
		if self.CheckOtherPhone(user):
			return False
		return True
		
	def Update(self, user):
		user.myuser.PersonID.CNIC = self.cleaned_data.get('CNIC')
		user.myuser.PersonID.Phone = self.cleaned_data.get('Phone')
		user.myuser.PersonID.FullName = self.cleaned_data.get('FullName')
		user.myuser.PersonID.save()
		
	
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
		

