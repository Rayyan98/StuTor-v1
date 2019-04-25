from django.contrib import admin
from .models import Person, CUser, Broker, Student , MyUser, Day, Qualification, Timming, Tutor, Subject, Board, TutorSubjects, Messages

from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User


# Register your models here.




admin.site.register(Messages)
admin.site.register(Person)
admin.site.register(MyUser)
admin.site.register(CUser)
admin.site.register(Broker)
admin.site.register(Student)
admin.site.register(Day)
admin.site.register(Qualification)
admin.site.register(Tutor)
admin.site.register(Timming)
admin.site.register(Subject)
admin.site.register(Board)
admin.site.register(TutorSubjects)

