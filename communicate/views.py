import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView

from communicate.help_logic import get_comment_tree
from communicate.models import CourseReview, Comment
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


class GetCommentsView(View):
    def get(self, request, module_id):
        threads = Comment.objects.filter(module_id=module_id, replies_to=None)
        result_dict = {}
        for t in threads:
            tread_tree = get_comment_tree(t, request.user)
            result_dict[f'comment_{t.id}'] = tread_tree
            #result_dict[f'comment_{t.id}']['replies'] = tread_tree

        return HttpResponse(json.dumps(result_dict))
