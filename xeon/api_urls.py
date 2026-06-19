from django.urls import path
from .api_views import (
    api_course_purchases,
    api_dashboard_calendar,
    api_dashboard_community_growth,
    api_dashboard_revenue,
    api_dashboard_stats,
)

urlpatterns = [
    path('dashboard/stats/', api_dashboard_stats, name='api_dashboard_stats'),
    path('dashboard/revenue/', api_dashboard_revenue, name='api_dashboard_revenue'),
    path('dashboard/calendar/', api_dashboard_calendar, name='api_dashboard_calendar'),
    path('dashboard/community-growth/', api_dashboard_community_growth, name='api_dashboard_community_growth'),
    path('dashboard/course-purchases/', api_course_purchases, name='api_course_purchases'),
]
