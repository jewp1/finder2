from django.urls import path

from apps.likes.views import LikeMatchesView, LikeProjectView, LikeUserView, UserLikedByView, UserLikesView

urlpatterns = [
    # Static paths MUST come before parametric to avoid Django treating
    # "likes" and "liked-by" as integers.
    path("likes/user/likes", UserLikesView.as_view()),
    path("likes/user/liked-by", UserLikedByView.as_view()),
    path("likes/user/<int:user_id>", LikeUserView.as_view()),
    path("likes/project/<int:project_id>", LikeProjectView.as_view()),
    path("likes/matches", LikeMatchesView.as_view()),
]
