from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_path = models.CharField(max_length=255)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, storage_path=instance.username.lower())


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=255)
    url_id = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.url_id = uuid.uuid4()
        super(Share, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + ': ' + self.path