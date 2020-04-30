from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from account.models import Profile
from content.models import Article, Tag


class Organization(models.Model):
    picture = models.ImageField(
        upload_to='pictures/organization',
        default='default_pic/organization.png',
        null=True,
        blank=True,
    )
    name = models.CharField(
        _('Organization Name'),
        max_length=128,
    )

    description = models.TextField(
        _('Organization description'),
        max_length=280,
        blank=True,
        null=True,
    )

    profiles = models.ManyToManyField(Profile, blank=True)
    head = models.OneToOneField(
        Profile,
        on_delete=models.SET_NULL,
        related_name='head',
        null=True,
        blank=True,
    )

    articles = models.ManyToManyField(Article, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    sub_org = models.ManyToManyField("self", blank=True,)

    def __str__(self):
        return self.name

    @property
    def color(self):
        from rating.models import FlexibleScale
        ct = ContentType.objects.get(model__iexact=self.__class__.__name__)
        try:
            rating = FlexibleScale.objects.get(
                content_type=ct,
                object_id=self.id
            )
            return rating.color
        except FlexibleScale.DoesNotExist:
            return "blue"

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')


class Post(models.Model):
    name = models.TextField(
        _('Post name'),
        max_length=256,
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
