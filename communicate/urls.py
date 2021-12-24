from django.urls import path

from communicate import views

urlpatterns = [
    path('course/<course_id>/add_review/',
         views.CreateReviewView.as_view(),
         name='create_review'),
    path('course/delete_review/<pk>/',
         views.DeleteReviewView.as_view(),
         name='delete_review'),
    path('course/module/<module_id>/get_comments/',
         views.GetCommentsView.as_view(),
         name='get_comments'),
    path('comment/<comment_id>/add_comment_vote/<vote_type>/',
         views.AddCommentVoteView.as_view(),
         name='add_comment_vote'),
    path('comment/<comment_id>/delete_comment_vote/',
         views.DeleteCommentVoteView.as_view(),
         name='delete_comment_vote'),
    path('comment/<comment_id>/change_comment_vote/',
         views.ChangeCommentVoteView.as_view(),
         name='change_comment_vote'),
    path('module/<module_id>/add_comment/',
         views.AddCommentView.as_view(),
         name='add_comment'),
    path('comment/<comment_id>/edit_comment/',
         views.EditCommentView.as_view(),
         name='edit_comment'),
]
