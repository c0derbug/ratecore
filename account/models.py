import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from content.models import Article, Comment, Tag
from rating.models import ContentRating, FlexibleScale, RatingCategory

# from .pipeline import update_profile


class UserManager(BaseUserManager):
    def create_user(self, password=None, **kwargs):
        data = self.model.init_kwargs(self.model, kwargs)
        user = self.model(**data)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, **kwargs):
        user = self.create_user(password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('Username'),
        max_length=24,
        unique=True,
        blank=True,
    )
    email = models.EmailField(
        _('Email'),
        unique=True,
    )
    # phone_number

    date_joined = models.DateTimeField(
        _('Date joined'),
        auto_now_add=True,
    )

    is_active = models.BooleanField(
        _('Active'),
        default=True,
    )
    is_staff = models.BooleanField(
        _('Staff'),
        default=False,
    )

    def __str__(self):
        return self.username

    def init_kwargs(self, arg_dict):
        return {
            k: v for k, v in arg_dict.items() if k in [f.name for f in self._meta.get_fields()]
        }

    def get_profile(self):
        try:
            return Profile.objects.get(user=self)
        except Profile.DoesNotExist:
            return None

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    picture = models.ImageField(
        upload_to='pictures/profile',
        default='default_pic/profile.png',
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        _('First name'),
        max_length=32,
    )
    middle_name = models.CharField(
        _('Middle name'),
        max_length=32,
        blank=True,
        default=''
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=32,
    )
    description = models.TextField(
        _('Profile description'),
        max_length=280,
        blank=True,

    )

    posts = models.ManyToManyField(
        'organization.Post',
        blank=True,
    )
    articles = models.ManyToManyField(Article, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def comments(self):
        ct_model = ContentType.objects.get(model__iexact=self.__class__.__name__)
        cmnts = Comment.objects.filter(
            content_type=ct_model,
            object_id=self.id
        )
        return cmnts.count()

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

    @property
    def publications(self):
        return self.articles.count()

    def __str__(self):
        if self.first_name and self.last_name:
            return '%s %s %s' % (
                self.last_name,
                self.first_name,
                self.middle_name
            )
        return 'Profile %s' % self.user

    @receiver(post_save, sender=User)
    def create_profile(instance, created, **kwargs):
        if created:
            try:
                Profile.objects.create(user=instance)
            except Exception:
                return None

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


@receiver(post_save, sender=Profile)
def create_scale(sender, instance, created, **kwargs):
    if created:
        obj = FlexibleScale(
            content_object=instance
        )
        obj.category, created = RatingCategory.objects.get_or_create(name='Harm')
        obj.save()
        return obj


@receiver(post_save, sender=Profile)
def create_content_rating(sender, instance, created, **kwargs):
    if created:
        obj = ContentRating(
            content_object=instance
        )
        obj.save()
        return obj