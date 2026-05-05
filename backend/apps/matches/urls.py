from django.urls import path
from apps.matches.views import (
    MatchListView,
    PotentialMatchesView,
    CreateMatchView,
    UpdateMatchStatusView,
)

urlpatterns = [
    path('matches/', MatchListView.as_view()),
    path('matches/potential', PotentialMatchesView.as_view()),
    path('matches/<int:match_id>/status', UpdateMatchStatusView.as_view()),
    path('matches/<int:user_id>', CreateMatchView.as_view()),
]
