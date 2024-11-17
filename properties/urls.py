from django.urls import path
from .views import PropertyListCreate, PropertyRetrieveUpdateDestroy, PropertyRecover

urlpatterns = [
    path("properties/", PropertyListCreate.as_view(), name="property-list-create"),
    path(
        "properties/<int:pk>/",
        PropertyRetrieveUpdateDestroy.as_view(),
        name="property-detail",
    ),
    path(
        "properties/<int:pk>/recover/",
        PropertyRecover.as_view(),
        name="property-recover",
    ),
]
