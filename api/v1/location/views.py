from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import *
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import serializers

from api.v1.location.serializers import *
from api.v1.account.serializers import *
from api.v1.organization.serializers import *
from api.v1.content.serializers import *
from location.models import Country


class LocationView(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    lookup_field = 'ISO_3166_1'
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        obj = get_object_or_404(self.queryset, ISO_3166_1__numeric=self.kwargs["ISO_3166_1"])
        return obj

    @action(detail=True)
    def cities(self, request, *args, **kwargs):
        if 'city_id' in kwargs:
            if 'action' in kwargs:
                try:
                    return getattr(self, kwargs['action'])(request, *args, **kwargs)
                except:
                    return Response(data=None, status=status.HTTP_404_NOT_FOUND)
            serializer = CitySerializer(City.objects.get(id=kwargs['city_id']))
            return Response(serializer.data)
        obj = self.get_object()
        serializer = CitySerializer(obj.cities.all(), many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True)
    def profiles(self, request, *args, **kwargs):

        if 'city_id' in kwargs:
            obj = City.objects.get(id=kwargs['city_id'])
            serializer = ProfileSerializer(obj.profiles.all(), many=True, context={"request": request})
            return Response(serializer.data)

        obj = self.get_object()
        serializer = list()
        for i in obj.cities.all():
            serializer.extend(ProfileSerializer(i.profiles.all(), many=True, context={"request": request}).data)
        return Response(serializer)

    @action(detail=True)
    def organizations(self, request, *args, **kwargs):

        if 'city_id' in kwargs:
            obj = City.objects.get(id=kwargs['city_id'])
            serializer = OrganizationSerializer(obj.organizations.all(), many=True, context={"request": request})
            return Response(serializer.data)

        obj = self.get_object()
        serializer = list()
        for i in obj.cities.all():
            serializer.extend(OrganizationSerializer(i.organizations.all(), many=True, context={"request": request}).data)
        return Response(serializer)

    @action(detail=True)
    def articles(self, request, *args, **kwargs):

        # Get all articles from cities
        if 'city_id' in kwargs:
            obj = City.objects.get(id=kwargs['city_id'])
            serializer = ArticleSerializer(obj.articles.all().order_by('-id'), many=True, context={"request": request})
            return Response(serializer.data)

        # Get all articles from countries
        obj = self.get_object()
        articles = Article.objects.none()
        for i in obj.cities.all():
            articles = articles.union(i.articles.all())

        serializer = ArticleSerializer(articles.order_by('-id'), many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, url_path='articles_part/(?P<s>\d+)-(?P<e>\d+)')
    def articles_part(self, request, *args, **kwargs):

        # Get part articles from cities
        if 'city_id' in kwargs:
            obj = City.objects.get(id=kwargs['city_id'])
            serializer = ArticleSerializer(
                obj.articles.all().order_by('-id')[int(kwargs['s']):int(kwargs['e'])],
                many=True,
                context={"request": request})
            return Response(serializer.data)

        # Get part articles from countries
        obj = self.get_object()
        articles = Article.objects.none()
        for i in obj.cities.all():
            articles = articles.union(i.articles.all())
        serializer = ArticleSerializer(
            articles.order_by('-id')[int(kwargs['s']):int(kwargs['e'])],
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True)
    def get_total(self, request, *args, **kwargs):

        # Get total articles from cities
        if 'city_id' in kwargs:
            obj = City.objects.get(id=kwargs['city_id'])
            return Response(obj.articles.all().count())

        # Get total articles from countries
        obj = self.get_object()
        articles = Article.objects.none()
        for i in obj.cities.all():
            articles = articles.union(i.articles.all())
        return Response(articles.count())