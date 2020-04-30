from django.test import TestCase
from account.models import *

obj = User.objects.get(username='getrateagent')

Profile.objects.create(user=obj)