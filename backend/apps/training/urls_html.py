from django.urls import path

from .views_html import (
    TrainingManagePageView,
    TrainingMaterialDetailPageView,
    TrainingPageView,
    TrainingStatsPageView,
)

urlpatterns = [
    path("", TrainingPageView.as_view(), name="training_page"),
    path("stats/", TrainingStatsPageView.as_view(), name="training_stats_page"),
    path("manage/", TrainingManagePageView.as_view(), name="training_manage_page"),
    path(
        "material/<int:pk>/",
        TrainingMaterialDetailPageView.as_view(),
        name="training_material_detail_page",
    ),
]
