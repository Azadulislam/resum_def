from django.contrib import admin
from django.urls import path
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static

from resume import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.ProfileListView.as_view(), name="profile-list"),
    path("profiles/", views.ProfileListView.as_view(), name="profile-list"),
    path("profiles/create/", views.ProfileCreateView.as_view(), name="profile-create"),
    path("profiles/<uuid:pk>/", views.ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/<uuid:pk>/variation/", views.profile_variation_view, name="profile-variation"),
    path("profiles/<uuid:pk>/variation/<uuid:variation_id>/", views.profile_variation_view, name="profile-variation-selected"),
    path("profiles/<uuid:pk>/pdf/", views.profile_variation_pdf, name="profile-variation-pdf"),
    path("profiles/<uuid:pk>/update/", views.ProfileUpdateView.as_view(), name="profile-update"),
    path("profiles/<uuid:pk>/delete/", views.ProfileDeleteView.as_view(), name="profile-delete"),
    path("sections/", views.SectionListView.as_view(), name="section-list"),
    path("sections/create/", views.SectionCreateView.as_view(), name="section-create"),
    path("sections/<uuid:pk>/", views.SectionDetailView.as_view(), name="section-detail"),
    path("sections/<uuid:pk>/update/", views.SectionUpdateView.as_view(), name="section-update"),
    path("sections/<uuid:pk>/delete/", views.SectionDeleteView.as_view(), name="section-delete"),
    path("section-items/", views.SectionItemListView.as_view(), name="section-item-list"),
    path("section-items/create/", views.SectionItemCreateView.as_view(), name="section-item-create"),
    path("section-items/<uuid:pk>/", views.SectionItemDetailView.as_view(), name="section-item-detail"),
    path("section-items/<uuid:pk>/update/", views.SectionItemUpdateView.as_view(), name="section-item-update"),
    path("section-items/<uuid:pk>/delete/", views.SectionItemDeleteView.as_view(), name="section-item-delete"),
    path("variations/", views.VariationListView.as_view(), name="variation-list"),
    path("variations/create/", views.VariationCreateView.as_view(), name="variation-create"),
    path("variations/<uuid:pk>/", views.VariationDetailView.as_view(), name="variation-detail"),
    path("variations/<uuid:pk>/update/", views.VariationUpdateView.as_view(), name="variation-update"),
    path("variations/<uuid:pk>/delete/", views.VariationDeleteView.as_view(), name="variation-delete"),
] + debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)