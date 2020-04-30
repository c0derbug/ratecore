from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField

from account.models import Profile
from organization.models import Organization
from content.models import Article


class City(models.Model):
    picture = models.ImageField(
        upload_to='pictures/city',
        default='default_pic/city.png',
        null=True,
        blank=True,
    )
    name = models.CharField(
        _('City name'),
        max_length=64,
    )

    profiles = models.ManyToManyField(Profile, blank=True)
    organizations = models.ManyToManyField(Organization, blank=True)
    articles = models.ManyToManyField(Article, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')


class Country(models.Model):
    picture = models.ImageField(
        upload_to='pictures/country',
        default='default_pic/country.png',
        null=True,
        blank=True,
    )
    name = models.CharField(
        _('Country name'),
        max_length=64,
    )

    ISO_3166_1 = JSONField(
        _('ISO 3166-1'),
        default=dict,
        null=True,
        blank=True,
    )

    profiles = models.ManyToManyField(Profile, blank=True,)
    cities = models.ManyToManyField(City, blank=True,)
    organizations = models.ManyToManyField(Organization, blank=True,)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Country')
