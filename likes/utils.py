from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef

from .models import Like   

def annotate_liked_by_user(queryset, user, model):
    if not user.is_authenticated:
        return queryset.annotate(
            is_liked_by_user=Exists(Like.objects.none())
        )

    ct = ContentType.objects.get_for_model(model)
    likes = Like.objects.filter(
        user=user,
        content_type=ct,
        object_id=OuterRef('pk')
    )
    return queryset.annotate(is_liked_by_user=Exists(likes))


def is_liked_by(user, model, object_id):
    if not user.is_authenticated:
        return False
    ct = ContentType.objects.get_for_model(model)
    return Like.objects.filter(
        user=user, content_type=ct, object_id=object_id
    ).exists()

def like(user, model, object_id):
    ct = ContentType.objects.get_for_model(model)
    like, created  = Like.objects.get_or_create(
        user=user, content_type=ct, object_id=object_id
    )
    if not created:
        like.delete()
        return False
    return True 