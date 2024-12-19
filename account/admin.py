from django.contrib import admin
from .models import Relation, profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin 
# Register your models here.

class ProfileInline(admin.StackedInline):
    model = profile
    can_delete = False

class ExtendedUserAdmin(UserAdmin):
    inlines = (ProfileInline,)    


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)

admin.site.register(Relation)


