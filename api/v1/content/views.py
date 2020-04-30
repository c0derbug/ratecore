import os
import requests
import urllib3
from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType

from oauth2_provider.models import AccessToken
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from oauth2_provider.contrib.rest_framework import (
    IsAuthenticatedOrTokenHasScope, OAuth2Authentication,
)

from api.v1.content.serializers import ArticleSerializer, CommentSerializer
from content.models import Article, Comment, Tag
from content.service import get_favicon, get_picture
from rating.models import FlexibleScale, RatingCategory
from account.models import Profile


class ArticleView(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    serializer_class = ArticleSerializer
    list_allowed_methods = ['get', 'put']

    permission_classes_by_action = {
        '*': [AllowAny],
        'create': [IsAuthenticatedOrTokenHasScope],
        'list': [AllowAny],

    }
    required_scopes = ['read', 'write']

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = Article.objects.all()
        if 'in_parts' in self.request.query_params:
            parts = eval(self.request.query_params.get('in_parts'))
            if 'filtering' in self.request.query_params:
                filtering = eval(self.request.query_params.get('filtering'))
                if filtering['by'] == 'author':
                    author = Profile.objects.get(id=filtering['id']).user
                    queryset = Article.objects.filter(author=author)
            return queryset.order_by('-id')[int(parts['start']):int(parts['end'])]
        else:
            return queryset

    @action(detail=False, url_path='as_part/(?P<s>\d+)-(?P<e>\d+)')
    def as_part(self, request, *args, **kwargs):
        articles = Article.objects.all().order_by('-id')[int(kwargs['s']):int(kwargs['e'])]
        data = self.serializer_class(articles, many=True, context={"request": request})
        return Response(data.data)

    @action(detail=False, url_path='get-total')
    def get_total(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset.count())

    @action(detail=False)
    def get_favicon(self, request, *args, **kwargs):
        favicon_url = get_favicon(kwargs['link'])
        try:
            response = requests.get(favicon_url[0], stream=True)
            return Response(
                data={
                    'favicon': favicon_url[0]
                }
            )
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        img_file, file_path = get_picture(request.data['picture'])
        data = {
            'author': request.user.id,
            'picture': img_file,
            'title': request.data.get('title'),
            'text': request.data.get('text'),
            'source_link': request.data.get('source_link'),
        }
        serializer = self.serializer_class(data=data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            article = serializer.save()

            if 'tags' in request.data:
                for tag in request.data['tags']:
                    obj, created = Tag.objects.get_or_create(name=tag)
                    article.tags.add(obj)

            if 'scale' in request.data:
                scale_data = request.data.get('scale')
                scale_data['category'], created = RatingCategory.objects.get_or_create(name=request.data.get('scale')['category'])
                scale_data['content_object'] = article
                scale = FlexibleScale(**request.data.get('scale'))
                scale.save()

            headers = self.get_success_headers(serializer.data)
            os.remove(file_path)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(e)
            return Response()


class CommentView(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication]
    serializer_class = CommentSerializer

    permission_classes_by_action = {
        '*': [AllowAny],
        'create': [IsAuthenticatedOrTokenHasScope]

    }
    required_scopes = ['read', 'write']

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if 'model' in self.kwargs:
            ct_model = ContentType.objects.get(model=self.kwargs['model'])
            try:
                return Comment.objects.filter(
                    content_type=ct_model,
                    object_id=self.kwargs['id']
                ).order_by('-id')
            except Exception as e:
                return Comment.objects.all().order_by('-id')
        else:
            return Comment.objects.all().order_by('-id')

    @action(detail=False, url_path='get-part/(?P<s>\d+)-(?P<e>\d+)')
    def get_part(self, request, *args, **kwargs):
        comments = self.get_queryset()[int(kwargs['s']):int(kwargs['e'])]
        data = self.serializer_class(comments, many=True, context={"request": request}).data

        if not request.user.is_anonymous:
            for comment in comments:
                if request.user in comment.rating.up.all():
                    for cmnt in data:
                        if cmnt['id'] == comment.id:
                            cmnt['rating']['voted'] = 'up'
                elif request.user in comment.rating.down.all():
                    for cmnt in data:
                        if cmnt['id'] == comment.id:
                            cmnt['rating']['voted'] = 'down'
        return Response(data)

    @action(detail=False, url_path='get-total')
    def get_total(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset.count())

    def create(self, request, *args, **kwargs):
        ct_model = ContentType.objects.get(model=request.data.get('model')).id
        data = {
            'author': request.user.id,
            'text': request.data.get('text'),
            'content_type': ct_model,
            'object_id': request.data.get('id'),
        }

        serializer = self.serializer_class(data=data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
