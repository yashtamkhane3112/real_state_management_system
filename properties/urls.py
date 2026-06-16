from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.property_list, name="list"),
    path("new/", views.property_create, name="create"),
    path("approvals/", views.approvals_list, name="approvals_list"),
    path("city/<str:city>/", views.city_page, name="city"),
    path("market-pulse/", views.market_pulse, name="market_pulse"),
    path("<slug:slug>/", views.property_detail, name="detail"),
    path("<slug:slug>/edit/", views.property_update, name="update"),
    path("<slug:slug>/delete/", views.property_delete, name="delete"),
    path("<slug:slug>/approve/", views.approve_property, name="approve"),
    path("<slug:slug>/reject/", views.reject_property, name="reject"),
    path("<slug:slug>/sold/", views.mark_property_sold, name="mark_sold"),
    path("<slug:slug>/close/", views.mark_property_closed, name="mark_closed"),
    path("<slug:slug>/reopen/", views.reopen_property, name="reopen"),
    path("<slug:slug>/activate/", views.activate_property, name="activate"),
    path("<slug:slug>/submit/", views.submit_for_approval, name="submit"),
    # AI Features
    path("ai/match/", views.ai_property_match, name="ai_match"),
    path("<slug:slug>/ai/insights/", views.ai_property_insights, name="ai_insights"),
    path("<slug:slug>/ai/draft-inquiry/", views.ai_inquiry_draft, name="ai_draft_inquiry"),
]

