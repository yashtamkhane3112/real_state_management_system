from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from properties.models import Property
from properties.serializers import PropertySerializer

from .models import Favorite


class FavoriteViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PropertySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user).select_related("property")

    def list(self, request):
        favorites = self.get_queryset().select_related("property__category", "property__created_by").prefetch_related("property__amenities")
        properties = [f.property for f in favorites]
        page = self.paginate_queryset(properties)
        if page is not None:
            return self.get_paginated_response(PropertySerializer(page, many=True, context={"request": request}).data)
        return Response(PropertySerializer(properties, many=True, context={"request": request}).data)

    def create(self, request):
        slug = request.data.get("slug") or request.data.get("property_slug")
        prop = Property.objects.public().filter(slug=slug).first() if slug else None
        if not prop:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        return Response(
            {"detail": "Saved" if created else "Already saved", "slug": prop.slug, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["delete"], url_path=r"by-slug/(?P<slug>[^/]+)")
    def remove_by_slug(self, request, slug=None):
        prop = Property.objects.public().filter(slug=slug).first()
        if not prop:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
        Favorite.objects.filter(user=request.user, property=prop).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path=r"toggle/(?P<slug>[^/]+)")
    def toggle(self, request, slug=None):
        prop = Property.objects.public().filter(slug=slug).first()
        if not prop:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            favorite.delete()
            return Response({"detail": "Removed", "slug": slug, "is_favorite": False})
        return Response({"detail": "Saved", "slug": slug, "is_favorite": True}, status=status.HTTP_201_CREATED)
