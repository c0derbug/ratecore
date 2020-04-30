from rest_framework import serializers
from account.models import User, Profile
from api.v1.organization.serializers import OrganizationSerializer, PostSerializer


class ProfileSerializer(serializers.ModelSerializer):

    tags = serializers.StringRelatedField(many=True)
    posts = PostSerializer(many=True)

    # comments = CommentSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            'id',
            'picture',
            'color',
            'first_name',
            'middle_name',
            'last_name',
            'posts',
            'tags',
            'comments',
            'publications'
        )