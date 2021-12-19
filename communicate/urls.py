from django.urls import path

from communicate import views

urlpatterns = [
    path('course/<course_id>/add_review',
         views.CreateReviewView.as_view(),
         name='create_review'),
    path('course/delete_review/<pk>/',
         views.DeleteReviewView.as_view(),
         name='delete_review'),
]