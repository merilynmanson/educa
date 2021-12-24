import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView

from communicate.forms import CommentForm
from communicate.help_logic import get_comment_tree
from communicate.models import CourseReview, Comment, CommentVote
from courses.forms import ReviewForm
from courses.models import Course, Module


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
        threads = Comment.objects.filter(module_id=module_id, replies_to=None).order_by('-date')

        result_dict = {}
        for t in threads:
            tread_tree = get_comment_tree(t, request.user)
            result_dict[f'comment_{t.id}'] = tread_tree

        return HttpResponse(json.dumps(result_dict))


class AddCommentVoteView(View):
    def get(self, request, comment_id, vote_type):
        comment = Comment.objects.get(id=comment_id)
        if vote_type == 'like':
            is_like = True
        else:
            is_like = False
        print('REQUEST WAS RECEIVED!')
        CommentVote.objects.create(comment=comment,
                                   user=request.user,
                                   is_like=is_like)

        return HttpResponse(status=200)


class DeleteCommentVoteView(View):
    def get(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        vote = CommentVote.objects.get(user=request.user,
                                       comment=comment)
        vote.delete()
        return HttpResponse(status=200)


class ChangeCommentVoteView(View):
    def get(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        vote = CommentVote.objects.get(user=request.user,
                                       comment=comment)

        if vote.is_like:
            vote.is_like = False
        else:
            vote.is_like = True

        vote.save()
        return HttpResponse(status=200)


class AddCommentView(View):
    def post(self, request, module_id):
        new_comment = CommentForm(request.POST).save(commit=False)
        new_comment.user = request.user
        new_comment.module_id = module_id
        if 'replies_to' in request.POST:
            new_comment.replies_to = Comment.objects.get(id=int(request.POST['replies_to']))
        else:
            new_comment.replies_to = None

        new_comment.save()

        return HttpResponseRedirect(reverse_lazy('student_course_detail_module',
                                                 args=[Module.objects.get(id=module_id).course.id,
                                                       module_id]))


class EditCommentView(View):
    def post(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        if comment.user != request.user:
            return HttpResponse(status=403)

        comment.text = request.POST['text']
        comment.save()

        return HttpResponseRedirect(reverse_lazy('student_course_detail_module',
                                                 args=[comment.module.course.id,
                                                       comment.module.id]))
