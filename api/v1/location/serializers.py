from rest_framework import serializers
from location.models import *


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = (
            'id',
            'picture',
            'name',
            'ISO_3166_1',
        )


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            'id',
            'picture',
            'name',
        )