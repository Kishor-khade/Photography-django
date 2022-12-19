from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.conf import settings
from autoslug import AutoSlugField

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.png', upload_to='profile_pics')
	slug = AutoSlugField(populate_from='user')
	bio = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return str(self.user.username)

	def get_absolute_url(self):
		return "/users/{}".format(self.slug)

def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            pass

post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)

# Create your models here.
