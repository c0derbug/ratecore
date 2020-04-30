from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from oauth2_provider.contrib.rest_framework import (
    IsAuthenticatedOrTokenHasScope, OAuth2Authentication,
)

from django.contrib.contenttypes.models import ContentType

from api.v1.rating.serializers import FlexibleScaleSerializer, ContentRatingSerializer
from rating.models import FlexibleScale, ContentRating


class ScaleView(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    serializer_class = FlexibleScaleSerializer
    queryset = FlexibleScale.objects.all()

    permission_classes_by_action = {
        '*': [AllowAny],
        'to_vote': [IsAuthenticatedOrTokenHasScope]

    }
    required_scopes = ['read', 'write']

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    @action(detail=False, url_path='(?P<model>\D+)/(?P<id>\d+)')
    def object(self, request, *args, **kwargs):
        ct_model = ContentType.objects.get(model=kwargs['model'])
        obj = ct_model.model_class().objects.get(id=kwargs['id'])

        if not request.user.is_anonymous:
            profile = request.user.get_profile()
            if kwargs['model'] == 'profile' and kwargs['id'] == str(profile.id):
                return Response(data='Unable to get scale for %s' % kwargs['model'], status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            rating = FlexibleScale.objects.get(
                content_type=ct_model,
                object_id=kwargs['id']
            )
            data = self.serializer_class(rating).data
            if not request.user.is_anonymous:
                if request.user in rating.positive.all():
                    data['voted'] = 'positive'
                elif request.user in rating.indefinite.all():
                    data['voted'] = 'indefinite'
                elif request.user in rating.negative.all():
                    data['voted'] = 'negative'

            return Response(data)
        except FlexibleScale.DoesNotExist:
            return Response(data='Rating of %s not found' % kwargs['model'], status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, url_path='to-vote', methods=['post'])
    def to_vote(self, request, *args, **kwargs):
        field = getattr(self.get_object(), request.data.get('reaction'))
        field.add(request.user)
        self.get_object().save()
        data = self.serializer_class(self.get_object()).data
        data['voted'] = request.data.get('reaction')
        return Response(data)


class ContentRatingView(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    serializer_class = ContentRatingSerializer
    queryset = ContentRating.objects.all()

    permission_classes_by_action = {
        '*': [AllowAny],
        'to_vote': [IsAuthenticatedOrTokenHasScope]

    }
    required_scopes = ['read', 'write']

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    @action(detail=False, url_path='(?P<model>\D+)/(?P<id>\d+)')
    def object(self, request, *args, **kwargs):
        ct_model = ContentType.objects.get(model=kwargs['model'])
        if not request.user.is_anonymous:
            profile = request.user.get_profile()
            if kwargs['model'] == 'profile' and kwargs['id'] == str(profile.id):
                return Response(data='Unable to get scale for %s' % kwargs['model'], status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            rating = ContentRating.objects.get(
                content_type=ct_model,
                object_id=kwargs['id']
            )
            data = self.serializer_class(rating).data
            if not request.user.is_anonymous:
                if request.user in rating.up.all():
                    data['voted'] = 'up'
                elif request.user in rating.down.all():
                    data['voted'] = 'down'

            return Response(data)
        except FlexibleScale.DoesNotExist:
            return Response(data='Rating of %s not found' % kwargs['model'], status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, url_path='to-vote', methods=['post'])
    def to_vote(self, request, *args, **kwargs):
        field = getattr(self.get_object(), request.data.get('rate'))
        field.add(request.user)
        self.get_object().save()
        data = self.serializer_class(self.get_object(), context={"request": request}).data
        data['voted'] = request.data.get('rate')
        return Response(data)