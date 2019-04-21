from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewPersonForm, NewMyUserForm, NewUserForm, NewBrokerForm, NewTutorForm, 			NewTutorTimmingForm, NewTutorSubjectForm, NewStudentForm, NewGuardianForm, PasswordChange, ViewUserForm
from collections import OrderedDict
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout,authenticate
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, 		Subject, Board, TutorSubjects
from django.contrib.auth.models import User


# Create your views here.

############################################################################
##########--------------Tutor Registration---------------------------#######


def get_tutor_times(request):
	if not request.POST.getlist('Dayss'):
		messages.error(request , "Please specify atleast one day and time slot")
		return False
	Times = []
	days = request.POST.getlist('Dayss')
	for i in days:
		t1 = request.POST.get(i+'TimeStart')
		t2 = request.POST.get(i+'TimeEnd')
		if(t1 == ""):
			messages.error(request, "Start time is missing somewhere")
			return False
		elif(t2 == ""):
			messages.error(request, "End time is missing somewhere")
			return False
		else:
			try:
				t1 = datetime.strptime(t1, '%H %p')
				t2 = datetime.strptime(t2, '%H %p')
			except:
				messages.error(request, "Please use the time widget oversmart")
				return False
			if t2 - t1 < timedelta(hours = 1):
				messages.error(request, "End Time must be 1 hour ahead of Start Time")
				return False
			else:
				t1 = t1.time()
				t2 = t2.time()
				Times.append(t1)
				Times.append(t2)
	return (days, Times)


	
def get_tutor_subjects(request):
	g = request.POST.getlist('select')
	s = request.POST.getlist('select2')
	if not g:
		messages.error(request, "Please select atleast one general subject")
		return False
	if not s:
		messages.error(request, "Please select atleast one specific subject")
		return False
	g.extend(s)
	return g



def render_tutor_registration(request, revert = False):
	if(revert):	
		form1 = NewPersonForm(request.POST)
		form2 = NewMyUserForm(request.POST)
		form3 = NewUserForm(request.POST)
		form4 = NewTutorForm(request.POST)
	else:
		form1 = NewPersonForm
		form2 = NewMyUserForm
		form3 = NewUserForm
		form4 = NewTutorForm

	form1.field_order = ['CNIC', 'FullName', 'Phone']
	form3.field_order = ['email', 'username', 'password1', 'password2']
	form4.field_order = ['Highest_Qualification', 'Degree_Name', 'Institution',
							'Degree_Image']
	Days = Day.objects.all()
	General_Subjects = [i for i in Subject.objects.filter(Board__Name = 'Independent')]
	Specific_Subjects = [i for i in Subject.objects.all().exclude(Board__Name = 'Independent')]
	return render(request,
					'main/register_tutor.html',
					context = {'form1':form1, 'form2': form2, 'form3':form3,
								'form4':form4, 'Days':Days, 'General_Subjects':General_Subjects,
								'Specific_Subjects':Specific_Subjects,
								}
					)


		
def register_tutor(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	revert = False
	if(request.method == "POST"):
		newpersonform = NewPersonForm(request.POST)
		newmyuserform = NewMyUserForm(request.POST, request.FILES)
		newuserform = NewUserForm(request.POST)
		newtutorform = NewTutorForm(request.POST, request.FILES)
		times = get_tutor_times(request)
		all_subjects = get_tutor_subjects(request)
		if newpersonform.is_valid() == False:
			messages.error(request, "Phone number is already registered")
			revert = True
		elif newmyuserform.is_valid() == False:
			messages.error(request, "Image may not be present or is weird")
			revert = True
		elif (newuserform.is_valid() == False):
			messages.error(request, "Username taken or password mismatch")
			revert = True				
		elif newtutorform.is_valid() == False:
			messages.error(request, "Something wrong in degree details")
			revert = True						
		elif newuserform.IsEmailPresent():
			messages.error(request, 'Email is already registered')
			revert = True
		elif newpersonform.DoesCnicHaveAccount():
			messages.error(request, 'This CNIC already owned by account')
			revert = True
		elif newpersonform.DoesNumberHaveAccount():
			messages.error(request, 'This Phone number is already owned by account')
			revert = True
		elif request.POST.get('AgeCheckNewTutor') != "on":
			messages.warning(request, "Please certify that you are 18 years old or over")
			revert = True			
		elif not times:
			messages.info(request, "Please check your specidifed times")	
			revert = True
		elif not all_subjects:
			messages.info(request, "Please check subject specifications")
			revert = True
		else:
			newperson = newpersonform.SaveNewPerson()
			newuser  = newuserform.SaveNewUser(True)
			newmyuser = newmyuserform.SaveNewMyUser(newperson, newuser, "Pending", "Tutor")
			newtutor = newtutorform.SaveNewTutor(newmyuser)
			newtutorform.AddTutorSubjects(newtutor, all_subjects)
			newtutorform.AddTutorTimmings(newtutor, times[0], times[1])
			messages.success(request, "You have been registered successfully")
			return redirect("main:register_successful")
			
	return render_tutor_registration(request, revert)



##########################################################################
##########--------------Broker Registration------------------------#######


def register_broker(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	revert = False

	if request.method == "POST":
		user_form = NewUserForm(request.POST)
		myuser_form = NewMyUserForm(request.POST, request.FILES)
		person_form = NewPersonForm(request.POST)
		broker_form = NewBrokerForm()

		if person_form.is_valid() == False:
			messages.error(request, "Phone number is already registered")
			revert = True
		elif myuser_form.is_valid() == False:
			messages.error(request, "Image may not be present or is weird")
			revert = True
		elif (user_form.is_valid() == False):
			messages.error(request, "Username taken or password mismatch")
			revert = True				
		elif user_form.IsEmailPresent():
			messages.error(request, 'Email is already registered')
			revert = True
		elif person_form.DoesCnicHaveAccount():
			messages.error(request, 'This CNIC already owned by account')
			revert = True
		elif person_form.DoesNumberHaveAccount():
			messages.error(request, 'This Phone number is already owned by account')
			revert = True
		elif request.POST.get('AgeCheckNewBroker') != "on":
			messages.warning(request, "Please certify that you are 18 years old or over")
			revert = True
		else:
			newperson = person_form.SaveNewPerson()
			newuser  = user_form.SaveNewUser(True)
			newmyuser = myuser_form.SaveNewMyUser(newperson, newuser, "Pending", "CUser")
			newbroker = broker_form.SaveNewBroker(newmyuser)
			messages.success(request, "Registered succesfully")
			return redirect("main:register_successful")
		
	if(revert):
		person_form.field_order = ['CNIC', 'FullName', 'Phone']
		user_form.field_order = ['username', 'password1', 'password2', 'email']
		
		return render(request, 
					  'main/register_broker.html',
					  context={'form2':person_form,'form3':user_form, 'form4':myuser_form})
	else:
		form2 = NewPersonForm
		form2.field_order = ['CNIC', 'FullName', 'Phone']
		form4 = NewMyUserForm
		form3 = NewUserForm
		form3.field_order = [ 'email', 'username', 'password1', 'password2',]
		return render(request, 
					  'main/register_broker.html',
					  context={'form2':form2,'form3':form3, 'form4':form4})



##########################################################################
##########--------------Student Registration-----------------------#######


def render_student_registration(request, revert = False):
	if(revert):
		form1 = NewPersonForm(request.POST)
		form2 = NewUserForm(request.POST)
		form3 = NewMyUserForm(request.POST)
		form4 = NewGuardianForm(request.POST)
	else:
		form1 = NewPersonForm
		form2 = NewUserForm
		form3 = NewMyUserForm
		form4 = NewGuardianForm
	form1.field_order = ['CNIC', 'FullName', 'Phone']
	form2.field_order = ['email', 'username', 'password1', 'password2']
	form4.field_order = ['CNIC', 'FullName', 'Phone']
	return render(request, 
				  'main/register_student.html',
				  context={'form1':form1,'form3':form3,'form4':form4, 'form2':form2})
	


def register_student(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	revert = False
	
	if(request.method == 'POST'):
		person_form = NewPersonForm(request.POST)
		user_form = NewUserForm(request.POST)
		myuser_form = NewMyUserForm(request.POST, request.FILES)
		newguardianform = NewGuardianForm(request.POST)
		
		if person_form.is_valid() == False:
			messages.error(request, "Please have a look at your details again")
			revert = True
		elif user_form.is_valid() == False:
			messages.error(request, "Username taken or password mismatch")
			revert = True				
		elif user_form.IsEmailPresent():
			messages.error(request, 'Email is already registered')
			revert = True
		elif person_form.DoesCnicHaveAccount():
			messages.error(request, 'This CNIC already owned by account')
			revert = True
		elif person_form.DoesNumberHaveAccount():
			messages.error(request, 'This Phone number is already owned by account')
			revert = True
		elif myuser_form.is_valid() == False:
			# print(request.POST.get('Photograph'))
			# if(myuser_form.errors):
				# for msg in myuser_form.errors:			
					# messages.error(request, f"{msg}: {myuser_form.errors[msg]}")			
			messages.error(request, "Image may not be present or is weird")
			revert = True
		else:
			if request.POST.get('AgeCheckNewTutor') == "on":
				newperson = person_form.SaveNewPerson()
				newuser  = user_form.SaveNewUser(True)
				newmyuser = myuser_form.SaveNewMyUser(newperson, newuser, "Pending", "CUser")
				newstudentform = NewStudentForm()
				newstudent = newstudentform.SaveNewAdultStudent(newmyuser)
				messages.success(request, "Registered succesfully")
				return redirect("main:register_successful")
			elif newguardianform.is_valid() == True:
				newperson = person_form.SaveNewPerson()
				newuser  = user_form.SaveNewUser(True)
				newmyuser = myuser_form.SaveNewMyUser(newperson, newuser, "Pending", "CUser")
				guardian = newguardianform.SaveNewGuardian()
				newstudentform = NewStudentForm()
				newstudent = newstudentform.SaveNewMinorStudent(newmyuser, guardian)
				messages.success(request, "Registered succesfully")
				return redirect("main:register_successful")
			else:
				messages.warning(request, "Please certify that you are 18 years old or over, or provide guardian information")
				revert = True
	return render_student_registration(request, revert)



##########################################################################
##########--------------Handling Login and logout------------------#######


def login_request(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	if request.method == "POST":
		form = AuthenticationForm(request, data = request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username = username, password = password)
			if user is not None:
				myuser = MyUser.objects.filter(user = user).first()
				if (myuser.Status == "Pending"):
					messages.info(request, "Your register request is still pending approval")
					return render(request, 'main/login.html', {"form":form})
				elif (myuser.Status == "Go" or myuser.Status == 'Recheck'):
					login(request, user)
					request.session.set_expiry(0)
					messages.info(request, f"You are now logged in as {username}")
					return redirect('main:homepage')
				elif myuser.Status == "Declined":
					messages.error(request, "Your register request has been declined, Please contact help center is case of any further queries")
					return render(request, 'main/login.html', {"form":form})
				else:
					messages.error(request, "There was some weird error trying to log you in, Probably some typo, Contact admin to let you in")
					return render(request, 'main/login.html', {"form":form})
					
			else:
				messages.error(request, "Invalid username or password")
		else:
			username = request.POST.get('username')
			users = User.objects.filter(username = username)
			if users.count() > 0 and users.first().is_active == False:
				messages.info(request, "Your account is not active at the time")
			else:
				messages.error(request, "Invalid username or password")
						
	form = AuthenticationForm()
	return render(request, 'main/login.html',
					{'form':form})


def logout_request(request):
	logout(request)
	messages.info(request, "Logged out succesfully")
	return redirect("main:homepage")
	


##########################################################################
##########--------------Other Views--------------------------------#######

					
def register(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	return render(request, 'main/register.html'
					)


def homepage(request):
	return render(request, 
					'main/home.html')


def register_successful(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
		
	return render(request, 'main/register_successful.html')
	

def password_change(request):
	if not request.user.is_authenticated:
		return redirect("main:homepage")
	if request.method == 'POST':
		form = PasswordChange(request.POST)
		if form.is_valid():
			if form.cleaned_data.get('new_password') == form.cleaned_data.get('confirm_new_password'):
				user = authenticate(username = request.user, password = form.cleaned_data.get('old_password'))
				if user is not None :
					password = form.cleaned_data.get('new_password')
					user = User.objects.filter(username = request.user.username).first()
					user.set_password(password)
					user.save()
					user = authenticate(username = request.user, password = password)
					login(request, user)
					return password_change_done(request)
	form = PasswordChange
	return render(request, 'main/password_change_form.html', {'form':form})
	

def password_change_done(request):
	if not request.user.is_authenticated:
		return redirect("main:homepage")
	else:
		return render(request, 'main/password_change_done.html')


def view_account(request):
	if not request.user.is_authenticated:
		return redirect("main:homepage")
	if (request.user.myuser.Type == "Tutor"):
		messages.info(request, "Tutor")
		return view_tutor(request)
	elif request.user.myuser.Type == "CUser":
		if request.user.myuser.cuser.Type == "Student":
			messages.info(request, "Student")
			return view_student(request)
		elif request.user.myuser.cuser.Type == "Broker":
			messages.info(request, "Broker")
			return view_broker(request)
		else:
			messages.info(request, "Bad type in cuser")
	else:
		messages.info(request, "Bad type in myuser")
	return redirect("main:homepage")


def edit_account(request):
	if not request.user.is_authenticated:
		return redirect("main:homepage")
	if (request.user.myuser.Type == "Tutor"):
		messages.info(request, "Tutor")
		return edit_tutor(request)
	elif request.user.myuser.Type == "CUser":
		if request.user.myuser.cuser.Type == "Student":
			messages.info(request, "Student")
			return edit_student(request)
		elif request.user.myuser.cuser.Type == "Broker":
			messages.info(request, "Broker")
			return edit_broker(request)
		else:
			messages.info(request, "Bad type in cuser")
	else:
		messages.info(request, "Bad type in myuser")
	return redirect("main:homepage")


def edit_tutor(request):
	if request.method == 'POST':
		person_form = NewPersonForm(request.POST)
		user_form = ViewUserForm(request.POST)
		myuser_form = NewMyUserForm(request.POST, request.FILES)
		tutor_form = NewTutorForm(request.POST, request.FILES)
		person_form.is_valid()
		user_form.is_valid()
		times = get_tutor_times(request)
		all_subjects = get_tutor_subjects(request)
		if not person_form.Validate(request.user):
			messages.error(request, "something person failed 2")
		elif not user_form.Validate(request.user):
			messages.error(request, "something user failed")
		elif not times:
			messages.info(request, "Please check your specidifed times")
		elif not all_subjects:
			messages.info(request, "Please check subject specifications")
		else:
			person_form.Update(request.user)
			user_form.Update(request.user)
			if myuser_form.is_valid():
				myuser_form.Update(request.user)
			myuser_form.UpdateUserStatus(request.user, 'Recheck')
			if tutor_form.is_valid():
				tutor_form.UpdateFull(request.user)
			else:
				tutor_form.UpdatePartial(request.user)
			tutor_form.AddTutorTimmingsOverwrite(request.user, times[0], times[1])
			tutor_form.AddTutorSubjectsOverwrite(request.user, all_subjects)
			return redirect('main:view_account')
	return view_tutor(request, True)


def view_tutor(request, edit = False):
	if request.method == 'POST':
		return redirect('main:account_edit')
	person_form = NewPersonForm(instance = request.user.myuser.PersonID)
	user_form = ViewUserForm(instance = request.user)
	myuser_form = NewMyUserForm(instance = request.user.myuser)
	tutor_form = NewTutorForm(instance = request.user.myuser.tutor)
	if not edit:
		person_form.Freeze()
		user_form.Freeze()
		myuser_form.Freeze()
		tutor_form.Freeze()
	else:
		user_form.FreezePartial()
	Tutor_Subjects = [i.Subject.id for i in TutorSubjects.objects.filter(Tutor = request.user.myuser.tutor)]
	General_Subjects = Subject.objects.filter(Board__Name = 'Independent')
	Days = Day.objects.all()
	Tutor_Times = OrderedDict()
	for i in Days:
		t = Timming.objects.filter(Tutor = request.user.myuser.tutor, Day = i).first()
		if t is not None:
			Tutor_Times[i] = [1, t.TimeStart.strftime("%I %p"), t.TimeEnd.strftime("%I %p")]
		else:
			Tutor_Times[i] = [0]
	print(Tutor_Times)
	return render(request, 'main/view_tutor.html', {'person_form':person_form, 'user_form':user_form, 'myuser_form':myuser_form, 'edit':edit, 'tutor_form':tutor_form, 'General_Subjects':General_Subjects, 'Specific_Subjects':Subject.objects.exclude(Board__Name = 'Independent'), 'Days':Days, 'Tutor_Times':Tutor_Times, 'Tutor_Subjects':Tutor_Subjects})
	
	

def view_student(request):
	if request.method == 'POST':
		return redirect('main:account_edit')
	person_form = NewPersonForm(instance = request.user.myuser.PersonID)
	user_form = ViewUserForm(instance = request.user)
	myuser_form = NewMyUserForm(instance = request.user.myuser)
	guard = request.user.myuser.cuser.student.Guardian
	if guard is not None:
		guardian_form = NewGuardianForm()
		guardian_form.FillInstance(guard)
		guardian_form.Freeze()
		is_guardian = True
	else:
		guardian_form = None
		is_guardian = False
	person_form.Freeze()
	user_form.Freeze()
	myuser_form.Freeze()
	return render(request, 'main/view_student.html', {'person_form':person_form, 'user_form':user_form, 'myuser_form':myuser_form, 'edit':False, 'is_guardian':is_guardian,
	'guardian_form':guardian_form} )
	

def edit_student(request):
	if request.method == 'POST':
		person_form = NewPersonForm(request.POST)
		user_form = ViewUserForm(request.POST)
		myuser_form = NewMyUserForm(request.POST, request.FILES)
		user_form.is_valid()
		person_form.is_valid()
		if not person_form.Validate(request.user):
			messages.error(request, "something person failed 2")
		elif not user_form.Validate(request.user):
			messages.error(request, "something user failed")
		else:
			person_form.Update(request.user)
			user_form.Update(request.user)
			if myuser_form.is_valid():
				myuser_form.Update(request.user)
			myuser_form.UpdateUserStatus(request.user, 'Recheck')
			if request.user.myuser.cuser.student.Guardian is not None:
				guardian_form = NewGuardianForm(request.POST)
				guardian_form.is_valid()
				guardian_form.Update(request.user)
			return redirect('main:view_account')
	person_form = NewPersonForm(instance = request.user.myuser.PersonID)
	user_form = ViewUserForm(instance = request.user)
	myuser_form = NewMyUserForm(instance = request.user.myuser)
	guard = request.user.myuser.cuser.student.Guardian
	if guard is not None:
		guardian_form = NewGuardianForm()
		guardian_form.FillInstance(guard)
		is_guardian = True
	else:
		guardian_form = None
		is_guardian = False
	user_form.FreezePartial()
	return render(request, 'main/view_student.html', {'person_form':person_form, 'user_form':user_form, 'myuser_form':myuser_form, 'edit':True, 'is_guardian':is_guardian,
	'guardian_form':guardian_form} )
		

def view_broker(request):
	if request.method == 'POST':
		return redirect('main:account_edit')
	person_form = NewPersonForm(instance = request.user.myuser.PersonID)
	user_form = ViewUserForm(instance = request.user)
	myuser_form = NewMyUserForm(instance = request.user.myuser)
	person_form.Freeze()
	user_form.Freeze()
	myuser_form.Freeze()
	return render(request, 'main/view_broker.html', {'person_form':person_form, 'user_form':user_form, 'myuser_form':myuser_form, 'edit':False} )
	

def edit_broker(request):
	if request.method == 'POST':
		person_form = NewPersonForm(request.POST)
		user_form = ViewUserForm(request.POST)
		myuser_form = NewMyUserForm(request.POST, request.FILES)
		user_form.is_valid()
		person_form.is_valid()
		if not person_form.Validate(request.user):
			messages.error(request, "something person failed 2")
		elif not user_form.Validate(request.user):
			messages.error(request, "something user failed")
		else:
			person_form.Update(request.user)
			user_form.Update(request.user)
			if myuser_form.is_valid():
				myuser_form.Update(request.user)
			myuser_form.UpdateUserStatus(request.user, 'Recheck')
			return redirect('main:view_account')
	person_form = NewPersonForm(instance = request.user.myuser.PersonID)
	user_form = ViewUserForm(instance = request.user)
	user_form.FreezePartial()
	myuser_form = NewMyUserForm(instance = request.user.myuser)
	return render(request, 'main/view_broker.html', {'person_form':person_form, 'user_form':user_form, 'myuser_form':myuser_form, 'edit':True} )

	
##------------------------------------------------------------------##
## Helper Functions

