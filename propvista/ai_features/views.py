from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from rest_framework import decorators, permissions, response, viewsets

from .services import gemini_or_fallback


AI_FEATURES = [
    ("property_description_generator", "tab-description", ["prompt", "city", "audience"]),
    ("property_summary_generator", "tab-summary", ["prompt", "city"]),
    ("listing_improvement_suggestions", "tab-improvements", ["prompt", "city"]),
    ("basic_recommendations", "tab-recommendations", ["prompt", "audience"]),
]


@login_required
def ai_tools(request):
    return render(request, "dashboards/ai_tools.html", {"ai_features": AI_FEATURES})


@require_POST
@login_required
def generate(request, feature):
    return JsonResponse({"result": gemini_or_fallback(feature, request.POST.dict())})


class AIFeatureViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None

    def _run(self, request, feature):
        return response.Response({"feature": feature, "result": gemini_or_fallback(feature, request.data)})

    @decorators.action(detail=False, methods=["post"])
    def description(self, request):
        return self._run(request, "property_description_generator")

    @decorators.action(detail=False, methods=["post"])
    def summary(self, request):
        return self._run(request, "property_summary_generator")

    @decorators.action(detail=False, methods=["post"])
    def improvements(self, request):
        return self._run(request, "listing_improvement_suggestions")

    @decorators.action(detail=False, methods=["post"])
    def recommendations(self, request):
        return self._run(request, "basic_recommendations")

