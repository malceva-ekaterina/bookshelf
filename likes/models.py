from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    content_object = GenericForeignKey('content_type', 'object_id')
    

    class Meta:
        unique_together = ('user','content_type', 'object_id')

    def __str__(self):
        return f'Liked by {self.user.username} at {self.created_at}'