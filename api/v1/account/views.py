from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from oauth2_provider.models import AccessToken
from django.contrib.contenttypes.models import ContentType

from account.models import Profile
from api.v1.account.serializers import ProfileSerializer
from api.v1.content.serializers import CommentSerializer, ArticleSerializer
from content.models import Comment


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (permissions.AllowAny,)

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

    @action(detail=False, url_path='get-by-token/(?P<token>\w+)')
    def get_by_token(self, request, *args, **kwargs):
        user = AccessToken.objects.get(token=kwargs["token"]).user
        return Response(self.serializer_class(user.get_profile(), context={"request": request}).data)
