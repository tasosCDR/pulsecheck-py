from __future__ import annotations

from django.urls import path  # type: ignore
from .views import make_views


def make_urlpatterns(registry, *, base_path: str = "health/"):
    health_view, ready_view = make_views(registry)

    return [
        path(base_path, health_view),
        path(base_path + "live/", health_view),
        path(base_path + "ready/", ready_view),
    ]
