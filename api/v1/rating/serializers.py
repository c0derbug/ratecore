from rest_framework import serializers
from rating.models import FlexibleScale, ContentRating


class FlexibleScaleSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = FlexibleScale
        fields = (
            'id',
            'qns',
            'pos_ans',
            'indef_ans',
            'neg_ans',
            'pos',
            'indef',
            'neg',
            'color',
            'category',
        )


class ContentRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentRating
        fields = (
            'id',
            'up',
            'down',
            'ups',
            'downs'
        )

