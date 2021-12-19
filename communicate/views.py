from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView

from communicate.models import CourseReview
from courses.forms import ReviewForm
from courses.models import Course


class CreateReviewView(CreateView):
    model = CourseReview

    def post(self, request, course_id):
        new_review = ReviewForm(request.POST).save(commit=False)
        new_review.user = request.user
        new_review.course = Course.objects.get(id=course_id)
        new_review.save()

        return HttpResponseRedirect(reverse('course_detail', kwargs={'slug': Course.objects.get(id=course_id).slug}))


class DeleteReviewView(DeleteView):
    model = CourseReview

    def get(self, request, pk):
        review = CourseReview.objects.get(id=pk)
        course_id = review.course.id
        review.delete()
        return HttpResponseRedirect(reverse('course_detail', kwargs={'slug': Course.objects.get(id=course_id).slug}))

