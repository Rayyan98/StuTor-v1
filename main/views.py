from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewPersonForm, NewMyUserForm, NewUserForm, NewBrokerForm, NewTutorForm, NewTutorTimmingForm, NewTutorSubjectForm
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout,authenticate
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, Subject, Board, TutorSubjects
from django.contrib.auth.models import User


# Create your views here.

def homepage(request):
	return render(request, 
					'main/home.html')
		
		
def register_tutor(request):
	revert = False
	if(request.method == "POST"):
		if False:
			pass
		elif not request.POST.getlist('Dayss'):
			messages.error(request , "Please specify atleast one day and time slot")
			revert = True
		else:
			Times = []
			for i in request.POST.getlist('Dayss'):
				t1 = request.POST.get(i+'TimeStart')
				t2 = request.POST.get(i+'TimeEnd')
				if(t1 == ""):
					messages.error(request, "Start time is missing somewhere")
					revert = True
					break
				elif(t2 == ""):
					messages.error(request, "End time is missing somewhere")
					revert = True
					break
				else:
					t1 = datetime.strptime(t1, '%I:%M %p')
					t2 = datetime.strptime(t2, '%I:%M %p')
					if t2 - t1 < timedelta(hours = 1):
						messages.error(request, "End Time must be 1 hour ahead of Start Time")
						revert = True
						break
					else:
						messages.info(request, "Add code")
			
	if(revert):
		form1 = NewPersonForm
		form2 = NewMyUserForm
		form3 = NewUserForm
		form4 = NewTutorForm
		form5 = NewTutorSubjectForm
		form6 = NewTutorTimmingForm
		Days = Day.objects.all()
		return render(request,
						'main/register_tutor.html',
						context = {'form1':form1, 'form2': form2, 'form3':form3,
									'form4':form4, 'form5':form5, 'form6': form6,
									'Days':Days}
						)
	else:
		form1 = NewPersonForm
		form2 = NewMyUserForm
		form3 = NewUserForm
		form4 = NewTutorForm
		form5 = NewTutorSubjectForm
		form6 = NewTutorTimmingForm
		Days = Day.objects.all()
		return render(request,
						'main/register_tutor.html',
						context = {'form1':form1, 'form2': form2, 'form3':form3,
									'form4':form4, 'form5':form5, 'form6': form6,
									'Days':Days}
						)



def register_student(request):
	form2 = NewPersonForm
	form2.field_order = ['CNIC', 'FullName', 'Phone']
	form3 = NewMyUserForm
	form3.field_order = ['Email', 'Pic', 'username', 'password1', 'password2']
	form4 = NewPersonForm
	form4.field_order = ['CNIC', 'FullName', 'Phone']	
	return render(request, 
				  'main/register_student.html',
				  context={'form2':form2,'form3':form3,'form4':form4})




				 
def register_broker(request):
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
		form3.field_order = ['username', 'password1', 'password2', 'email']
		return render(request, 
					  'main/register_broker.html',
					  context={'form2':form2,'form3':form3, 'form4':form4})


def login_request(request):
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
				elif (myuser.Status == "Go"):
					login(request, user)
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

					
def register(request):
	return render(request, 'main/register.html'
					)


def logout_request(request):
	logout(request)
	messages.info(request, "Logged out succesfully")
	return redirect("main:homepage")
	

def register_successful(request):
	return render(request, 'main/register_successful.html')
	
##------------------------------------------------------------------##
## Helper Functions

