from django.contrib.auth.models import User
from django.db import models

from courses.models import Course, Module


class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    text = models.TextField(max_length=500)
    like = models.BooleanField()

    class Meta:
        unique_together = ('user', 'course')


class Comment(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    text = models.TextField()
    replies_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='replies')


class CommentVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('user', 'comment')