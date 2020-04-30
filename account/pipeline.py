import os
import random
import urllib.request
from django.db import IntegrityError

from uuid import uuid4
from social_core.utils import slugify, module_member
from django.core.files import File

from account.models import *
from location.models import *
from rating.models import *

USER_FIELDS = ['username', 'email']


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    if 'username' not in backend.setting('USER_FIELDS', USER_FIELDS):
        return
    storage = strategy.storage

    if not user:

        if backend.name == 'mailru-oauth2':
            mailru_username = details.get('email').split("@")[0]
            return {'username': mailru_username}

        email_as_username = strategy.setting('USERNAME_IS_FULL_EMAIL', False)
        uuid_length = strategy.setting('UUID_LENGTH', 16)
        max_length = storage.user.username_max_length()
        do_slugify = strategy.setting('SLUGIFY_USERNAMES', False)
        do_clean = strategy.setting('CLEAN_USERNAMES', True)

        if do_clean:
            override_clean = strategy.setting('CLEAN_USERNAME_FUNCTION')
            if override_clean:
                clean_func = module_member(override_clean)
            else:
                clean_func = storage.user.clean_username
        else:
            clean_func = lambda val: val

        if do_slugify:
            override_slug = strategy.setting('SLUGIFY_FUNCTION')
            if override_slug:
                slug_func = module_member(override_slug)
            else:
                slug_func = slugify
        else:
            slug_func = lambda val: val

        if email_as_username and details.get('email'):
            username = details['email']
        elif details.get('username'):
            username = details['username']
        else:
            username = uuid4().hex

        short_username = (username[:max_length - uuid_length]
                          if max_length is not None
                          else username)
        final_username = slug_func(clean_func(username[:max_length]))

        # Generate a unique username for current user using username
        # as base but adding a unique hash at the end. Original
        # username is cut to avoid any field max_length.
        # The final_username may be empty and will skip the loop.
        while not final_username or \
                storage.user.user_exists(username=final_username):
            username = short_username + uuid4().hex[:uuid_length]
            final_username = slug_func(clean_func(username[:max_length]))
    else:
        final_username = storage.user.get_username(user)
    return {'username': final_username}


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}
    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    try:
        usr = User.objects.get(email=fields.get('email'))
        fields['username'] = usr.username
        return {
            'is_new': True,
            'user': strategy.create_user(**fields)
        }
    except User.DoesNotExist:
        try:
            username = fields.get('username')
            usr = User.objects.get(username=username)
            if usr.email != fields.get('email'):
                new_username = username + '_' + ''.join([random.choice(list('1234567890')) for x in range(4)])
                fields['username'] = new_username
                return {
                    'is_new': True,
                    'user': strategy.create_user(**fields)
                }
        except Exception:
            return {
                'is_new': True,
                'user': strategy.create_user(**fields)
            }
            # return {
            #     'is_new': True,
            #     'user': strategy.create_user(**fields)
            # }


def user_details(strategy, details, user=None, *args, **kwargs):
    """Update user details using data from provider."""
    if not user:
        return

    changed = False  # flag to track changes
    protected = ('username', 'id', 'pk', 'email') + \
                tuple(strategy.setting('PROTECTED_USER_FIELDS', []))

    # Update user model attributes with the new data sent by the current
    # provider. Update on some attributes is disabled by default, for
    # example username and id fields. It's also possible to disable update
    # on fields defined in SOCIAL_AUTH_PROTECTED_USER_FIELDS.
    for name, value in details.items():
        if value is None or not hasattr(user, name) or name in protected:
            continue

        # Check https://github.com/omab/python-social-auth/issues/671
        current_value = getattr(user, name, None)
        if current_value or current_value == value:
            continue

        changed = True
        setattr(user, name, value)

    if changed:
        strategy.storage.user.changed(user)


def save_profile(strategy, details, backend, user=None, *args, **kwargs):
    if not user:
        return

    profile = user.get_profile()
    if profile is None:
        profile = Profile(user=user)
    for k, v in details.items():
        setattr(profile, k, v)
    profile.save()


def get_picture_profile(backend, user, response, *args, **kwargs):
    if not user:
        return

    profile = user.get_profile()
    if backend.name == 'google-oauth2':
        if profile.picture != 'default_pic/profile.png':
            profile.picture.delete()
        image = urllib.request.urlretrieve(response.get('picture'))
        fname = os.path.basename(response.get('picture'))

        with open(image[0], 'rb') as fp:
            profile.picture.save(fname, File(fp), save=False)
            profile.save()
    if backend.name == 'yandex-oauth2':
        if not response.get('is_avatar_empty'):
            if profile.picture != 'default_pic/profile.png':
                profile.picture.delete()
            yapic = 'https://avatars.yandex.net/get-yapic/'
            img_url = yapic + response.get('default_avatar_id') + '/islands-200'
            image = urllib.request.urlretrieve(img_url)
            fname = os.path.basename(img_url)
            with open(image[0], 'rb') as fp:
                profile.picture.save(fname, File(fp), save=False)
                profile.save()
        else:
            if profile.picture != 'default_pic/profile.png':
                profile.picture.delete()
    if backend.name == 'mailru-oauth2':
        if profile.picture != 'default_pic/profile.png':
            profile.picture.delete()
        image = urllib.request.urlretrieve(response.get('pic_big'))
        fname = os.path.basename(response.get('pic_190'))
        with open(image[0], 'rb') as fp:
            profile.picture.save(fname, File(fp), save=False)
            profile.save()


def save_country(strategy, details, backend, user=None, *args, **kwargs):
    if not user:
        return

    profile = user.get_profile()
    if backend.name == 'google-oauth2':
        try:
            country = Country.objects.get(ISO_3166_1__alpha_2__iexact=kwargs.get('response').get('locale'))
            country.profiles.add(profile)
        except Country.DoesNotExist:
            try:
                country = Country.objects.get(ISO_3166_1__alpha_3__iexact=kwargs.get('response').get('locale'))
                country.profiles.add(profile)
            except Country.DoesNotExist:
                pass

