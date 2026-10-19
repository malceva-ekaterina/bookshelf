from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    city = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Profile {self.user.username}"
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.avatar.path)

        if img.height > 300 or img.width > 300:
            img.thumbnail((300, 300))
            img.save(self.avatar.path)

class Follow(models.Model):

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta():
        unique_together = ('follower', 'author')
    
    def __str__(self):
            return f"{self.follower.username} follow to {self.author.username}"