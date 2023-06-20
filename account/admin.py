from django.contrib import admin
from django.contrib.auth.models import Group

from account.models import EndUser, Batch

admin.site.register(EndUser)
admin.site.register(Batch)

admin.site.unregister(Group)
