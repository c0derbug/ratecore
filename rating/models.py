from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from content.models import Article, Comment


class RatingCategory(models.Model):
    name = models.CharField(
        _('Category name'),
        max_length=64,
    )
    question = models.CharField(
        _('Question'),
        max_length=240,
        blank=True,
        default='',
    )
    positive_answer = models.CharField(
        _('Positive answer'),
        max_length=240,
        blank=True,
    )
    indefinite_answer = models.CharField(
        _('indefinite answer'),
        max_length=240,
        blank=True,
    )
    negative_answer = models.CharField(
        _('Negative answer'),
        max_length=240,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Rating Category')
        verbose_name_plural = _('Rating Category')


class FlexibleScale(models.Model):
    question = models.CharField(
        _('Question'),
        max_length=240,
        blank=True,
        default='',
    )
    positive_answer = models.CharField(
        _('Positive answer'),
        max_length=240,
        blank=True,
    )
    indefinite_answer = models.CharField(
        _('indefinite answer'),
        max_length=240,
        blank=True,
    )
    negative_answer = models.CharField(
        _('Negative answer'),
        max_length=240,
        blank=True,
    )

    positive = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='pstv_r',
        verbose_name='Positive reactions',
        blank=True,
    )
    indefinite = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='indef_r',
        verbose_name='indefinite reactions',
        blank=True,
    )
    negative = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='ngtv_r',
        verbose_name='Negative reactions',
        blank=True,
    )

    category = models.ForeignKey(
        RatingCategory,
        verbose_name='Rate category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Relation with models through ForeignKey
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Content type',
    )
    object_id = models.PositiveIntegerField(
        verbose_name='Object ID'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def qns(self):
        model = self.content_type.model_class()
        if self.category.name != 'Custom':
            if model.__name__ == 'Profile':
                return self.category.question.format('Этот', 'человек')
            elif model.__name__ == 'Organization':
                return self.category.question.format('Эта', 'организация')
            elif model.__name__ == 'Article':
                return self.category.question.format('Это', 'событие')
        else:
            return self.question

    @property
    def pos_ans(self):
        if self.category.name != 'Custom':
            return self.category.positive_answer
        else:
            return self.positive_answer

    @property
    def indef_ans(self):
        if self.category.name != 'Custom':
            return self.category.indefinite_answer
        else:
            return self.indefinite_answer

    @property
    def neg_ans(self):
        if self.category.name != 'Custom':
            return self.category.negative_answer
        else:
            return self.negative_answer

    @property
    def pos(self):
        return self.positive.count()

    @property
    def indef(self):
        return self.indefinite.count()

    @property
    def neg(self):
        return self.negative.count()

    @property
    def color(self):
        a = self.pos
        b = self.indef
        c = self.neg
        if b >= a and b >= c or a == c:
            return 'blue'
        else:
            if a > c:
                return 'green'
            else:
                return 'red'

    @property
    def object(self):
        model = apps.get_model(app_label=self.content_type.app_label, model_name=self.content_type.model)
        obj = model.objects.get(id=self.object_id)
        return obj.__str__

    def __str__(self):
        model = self.content_type.model_class()
        try:
            return 'Rate of %s %s' % (model.__name__.lower(), model.objects.get(id=self.object_id))
        except Exception:
            return 'Rate of %s ' % self.id

    class Meta:
        verbose_name = _('Flexible Scale')
        verbose_name_plural = _('Flexible Scales')


class ContentRating(models.Model):
    up = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='up',
        verbose_name='Up content',
        blank=True,
    )
    down = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='down',
        verbose_name='Down content',
        blank=True,
    )

    # Relation with models through ForeignKey
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Content type',
    )
    object_id = models.PositiveIntegerField(
        verbose_name='Object ID'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def ups(self):
        return self.up.count()

    @property
    def downs(self):
        return self.down.count()

    def __str__(self):
        model = self.content_type.model_class()

        try:
            return 'rating of %s %s' % (model.__name__.lower(), model.objects.get(id=self.object_id))
        except Exception:
            return 'rating of %s' % self.object_id

    class Meta:
        verbose_name = _('Content rating')
        verbose_name_plural = _('Content ratings')


@receiver(post_save, sender=Article)
@receiver(post_save, sender=Comment)
def create_content_rating(sender, instance, created, **kwargs):
    if created:
        obj = ContentRating(
            content_object=instance
        )
        obj.save()
        return obj
