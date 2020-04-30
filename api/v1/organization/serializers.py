from rest_framework import serializers
from organization.models import *


class OrganizationSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)
    staff_count = serializers.SerializerMethodField('staff_counter')

    class Meta:
        model = Organization
        fields = (
            'id',
            'picture',
            'color',
            'name',
            'description',
            'staff_count',
            'tags',
        )

    @staticmethod
    def staff_counter(obj):
        return obj.profiles.all().count()


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'picture',
            'color',
            'first_name',
            'last_name',
        )


class PostSerializer(serializers.ModelSerializer):

    organization = OrganizationSerializer()

    class Meta:
        model = Post
        fields = (
            'id',
            'name',
            'organization',
        )