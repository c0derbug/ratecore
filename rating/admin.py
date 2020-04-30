from django.contrib import admin
from .models import *


# class UniversalEvaluationAdmin(admin.ModelAdmin):
#     fields = ['__all__']
#     list_display = ["id"]


admin.site.register(RatingCategory)
# admin.site.register(UniversalEvaluation)
admin.site.register(ContentRating)
# admin.site.register(OwnEvaluation)
admin.site.register(FlexibleScale)