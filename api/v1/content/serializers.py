from content.models import *
from rest_framework import serializers

from api.v1.account.serializers import ProfileSerializer
from api.v1.rating.serializers import ContentRatingSerializer
from account.models import Profile


class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            ''
            'picture',
            'first_name',
            'last_name',
            'color',
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class ArticleSerializer(serializers.ModelSerializer):
    author_profile = ProfileSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = (
            'id',
            'author',
            'author_profile',
            'picture',
            'source_link',
            'source_icon',
            'title',
            'text',
            'date_added',
            'tags',
            'comments',
            'short_rating'
        )
        extra_kwargs = {
            'author': {'write_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):

    author_profile = ProfileSerializer(required=False)
    rating = ContentRatingSerializer(required=False)

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'author_profile',
            'text',
            'date_added',
            'rating',
            'content_type',
            'object_id',
        ]
        extra_kwargs = {
            'content_type': {'write_only': True},
            'object_id': {'write_only': True},
        }

