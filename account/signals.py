from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import profile



@receiver(post_save, sender=User)
def createprofile(sender, **kwargs):
    if kwargs['created']:
        profile.objects.create(user=kwargs['instance'])
#post_save.connect(receiver=createprofile, sender=User)   