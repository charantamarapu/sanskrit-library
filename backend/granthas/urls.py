# granthas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GranthaViewSet, SuggestionViewSet

router = DefaultRouter()
router.register('granthas', GranthaViewSet)
router.register('suggestions', SuggestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]