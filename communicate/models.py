from django.contrib.auth.models import User
from django.db import models

from courses.models import Course


class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    text = models.TextField(max_length=500)
    like = models.BooleanField()

    class Meta:
        unique_together = ('user', 'course')


class Discussion(models.Model):
    pass


class Comment(models.Model):
    pass
