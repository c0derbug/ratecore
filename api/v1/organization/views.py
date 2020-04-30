from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from organization.models import Organization
from content.models import Comment
from api.v1.organization.serializers import OrganizationSerializer, StaffSerializer
from api.v1.content.serializers import CommentSerializer, ArticleSerializer


class OrganizationView(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    @action(detail=True)
    def staff_all(self, request, *args, **kwargs):
        staff = self.get_object().profiles.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def staff_short(self, request, *args, **kwargs):
        staff = self.get_object().profiles.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def comments(self, request, *args, **kwargs):
        comments = Comment.objects.filter(
            content_type=ContentType.objects.get(model__iexact=self.serializer_class.Meta.model.__name__),
            object_id=kwargs["pk"]
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def articles(self, request, *args, **kwargs):
        articles = self.get_object().articles.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)