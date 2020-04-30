import os
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.core.files import File
from django.dispatch import receiver

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from content.service import get_favicon, ico_to_png


class Tag(models.Model):

    name = models.CharField(
        _('Tag name'),
        max_length=64,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Article(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Article author',
    )
    picture = models.ImageField(
        upload_to='pictures/article',
        default='default_pic/article.png',
        null=True,
        blank=True,
    )
    title = models.CharField(
        _('Title'),
        max_length=240,
    )
    text = models.TextField(
        _('Text'),
    )
    date_added = models.DateTimeField(
        _('Date added'),
        auto_now_add=True,
    )

    source_link = models.URLField(
        _('Source Link'),
        blank=True,
        null=True,
    )
    source_icon = models.ImageField(
        _('Source icon'),
        upload_to='pictures/sources',
        default='default_pic/source.png',
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def author_profile(self):
        return self.author.get_profile()

    @property
    def short_rating(self):
        from rating.models import FlexibleScale
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            r = FlexibleScale.objects.get(
                content_type=ct,
                object_id=self.id
            )
            return dict(
                qns=r.qns,
                pos=r.pos,
                indef=r.indef,
                neg=r.neg,
            )
        except FlexibleScale.DoesNotExist:
            return None

    @property
    def comments(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        cmnts = Comment.objects.filter(
            content_type=ct,
            object_id=self.id
        )
        return cmnts.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')


@receiver(post_save, sender=Article)
def add_icon(instance, created, **kwargs):
    if created:
        try:
            article = Article.objects.get(id=instance.id)
            link = article.source_link

            icon_link, site = get_favicon(link)
            local_icon = ico_to_png(icon_link, site)

            site = local_icon.split('-', 1)[1].rsplit('.', 1)[0]
            path = settings.MEDIA_ROOT + '/pictures/sources/' + 'favicon-' + site + '.png'

            try:
                icon = open(path)
                article.source_icon = '/pictures/sources/' + 'favicon-' + site + '.png'
                article.save()
                os.remove(local_icon)
            except Exception as e:
                fname = os.path.basename(local_icon)
                with open(local_icon, 'rb') as fp:
                    article.source_icon.save(fname, File(fp), save=False)
                    article.save()
                    os.remove(local_icon)
        except Exception as e:
            return None


class Comment(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Comment author',
    )
    text = models.TextField(
        _('Text'),
        max_length=480,
    )
    date_added = models.DateTimeField(
        _('Date added'),
        auto_now_add=True,
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
        verbose_name='Object ID',
        null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def author_profile(self):
        return self.author.get_profile()

    @property
    def rating(self):
        from rating.models import ContentRating
        ct = ContentType.objects.get_for_model(self.__class__)
        rating = ContentRating.objects.get(content_type=ct, object_id=self.id)
        return rating

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
