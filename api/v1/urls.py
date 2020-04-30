from django.conf.urls import url, include
from django.urls import path
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from gandhi import settings

from api.v1.account.views import ProfileView
from api.v1.location.views import LocationView
from api.v1.rating.views import ScaleView, ContentRatingView
from api.v1.organization.views import OrganizationView
from api.v1.content.views import ArticleView, CommentView

router = DefaultRouter()
router.register(r'^profiles', ProfileView, base_name='ProfileView')
router.register(r'^locations', LocationView, base_name='LocationView')
router.register(r'^rating/scales', ScaleView, base_name='ScaleView')
router.register(r'^rating/ratings', ContentRatingView, base_name='ContentRatingView')
router.register(r'^organizations', OrganizationView, base_name='OrganizationView')
router.register(r'^content/articles', ArticleView, base_name='ArticleView')
router.register(r'^content/comments', CommentView, base_name='CommentView')
router.register(r'^content/comments/(?P<model>\D+)/(?P<id>\d+)', CommentView, base_name='CommentView')

cities = LocationView.as_view({
    'get': 'cities'
})
articles_part = LocationView.as_view({
    'get': 'articles_part'
})
get_favicon = ArticleView.as_view({
    'get': 'get_favicon'
})


urlpatterns = [
    url(r'^', include(router.urls)),

    # cities urls
    path('locations/<int:ISO_3166_1>/city/<int:city_id>/', cities, name='cities'),
    path('locations/<int:ISO_3166_1>/city/<int:city_id>/<str:action>/', cities, name='cities'),
    path('locations/<int:ISO_3166_1>/city/<int:city_id>/articles_part/<int:s>-<int:e>/', articles_part, name='articles_part'),
    path('content/articles/get_favicon/<path:link>/', get_favicon, name='get_favicon'),

    # path('content/comments/<str:model>/<int:id>/<int:start>-<int:end>/', CommentView, name='CommentView')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)