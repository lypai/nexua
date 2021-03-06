from django.db import models
from django.contrib.auth.models import User
# import uuid
from django.urls import reverse

from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver


icons = ('accdb', 'bmp', 'docx', 'eps',
         'gif', 'ind', 'jpeg', 'midi',
         'mp3', 'pdf', 'pptx', 'psd',
         'pub', 'tiff', 'url', 'wav',
         'wmv', 'zip', 'avi', 'css',
         'eml', 'fla', 'html', 'ini',
         'jsf', 'mov', 'mpeg', 'png',
         'proj', 'pst', 'rar', 'txt',
         'vsd', 'wma', 'xlsx')


def get_user_time(period):
    if period.days < 0:
        return "now"

    if period.days == 0:
        if period.seconds > 3600:
            return '{:d} hours'.format(period.seconds // 3600)
        elif period.seconds > 60:
            return '{:d} minutes'.format(period.seconds // 60)
        else:
            return '{:d} seconds'.format(period.seconds)
    else:
        if period.days > 364:
            return '{:d} years'.format(period.days // 364)
        elif period.days > 14:
            return '{:d} weeks'.format(period.days // 7)
        else:
            return '{:d} days'.format(period.days)


class File(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    file_name = models.CharField(max_length=50, help_text="Enter file name", verbose_name="File name")
    upload_date = models.DateTimeField(verbose_name="Date of file upload")
    time_to_live = models.DateTimeField(verbose_name="Delete Date", blank=True, null=True)
    file_type = models.CharField(max_length=50, help_text="Enter file type", verbose_name="File type")
    size = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_itself = models.FileField()

    def __str__(self):
        return 'id: %s  name: %s date: %s type: %s size: %s user: %s ttl: %s' % (self.id, self.file_name, self.upload_date, self.file_type, self.size, self.user.__str__(), self.time_to_live)

    def get_absolute_url(self):
        return reverse('file-detail', args=[str(self.id)])

    def get_fullname(self):
        return '%s.%s' % (self.file_name, self.file_type)

    def get_size(self):
        if self.size // 1073741824:
            return '{:01.2f} Gb'.format(self.size / 1073741824)
        elif self.size // 1048576:
            return '{:01.2f} Mb'.format(self.size / 1048576)
        elif self.size // 1024:
            return '{:01.2f} Kb'.format(self.size / 1024)
        else:
            return '{:d} Bytes'.format(self.size)

    def get_time_to_delete(self):
        if self.time_to_live:
            period = self.time_to_live - timezone.now()

            return get_user_time(period)

    def get_upload_time(self):
        period = timezone.now() - self.upload_date
        return get_user_time(period)

    def get_logo(self):
        if self.file_type in icons:
            return 'img/icons/{}.png'.format(self.file_type)
        else:
            return 'img/icons/other.png'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def get_join_time(self):
        period = timezone.now() - self.user.date_joined

        return get_user_time(period)
