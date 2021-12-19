import json

from braces.views import JsonRequestResponseMixin, CsrfExemptMixin
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, CreateView, DetailView
from django.views.generic.base import TemplateResponseMixin, View
from django.http.response import HttpResponse, Http404

from communicate.models import CourseReview
from courses.forms import ModuleFormSet, TestItemsFormSet, TestForm, ReviewForm
from courses.help_logic import get_tests_for_module
from courses.models import Course, Module, Content, Subject, Test, FinishedModule, DoneTest, UsersTestItems
from students.forms import CourseEnrollForm


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])

        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)

        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class TestCreateUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/content/test_form.html'
    obj = None
    module = None

    def dispatch(self, request, module_id, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        if id:
            self.obj = get_object_or_404(Test,
                                         id=id,
                                         owner=request.user)

        return super().dispatch(request, module_id, id)

    def get(self, request, module_id, id=None):
        if id:
            test_form = TestForm(instance=Test.objects.get(id=id))
        else:
            test_form = TestForm()
        items_from = TestItemsFormSet(instance=self.obj)
        forms = [test_form, items_from]
        return self.render_to_response({'forms': forms,
                                        'object': self.obj})

    def post(self, request, module_id, id=None):
        test_form = TestForm(request.POST)
        test = None
        if test_form.is_valid():
            test = test_form.save(commit=False)
            test.owner = request.user
            test.module = self.module
            test.save()
            if not id:
                Content.objects.create(module=self.module,
                                       item=test)

                self.obj = test
            else:
                self.obj.title = test.title
                self.obj.save()

        items_form = TestItemsFormSet(instance=self.obj, data=request.POST)
        if items_form.is_valid():
            print("ITEMS VALID")
            items_form.save()

            return redirect('module_content_list', self.module.id)

        forms = [test_form, items_form]
        return self.render_to_response({'forms': forms,
                                        'object': self.obj})


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)

        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = "courses/course/list.html"

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(
            total_courses=Count('courses')
        )
        courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        if subject:
            subject = get_object_or_404(Subject,
                                        slug=subject)
            courses = courses.filter(subject=subject)

        return self.render_to_response({'subjects': subjects,
                                        'courses': courses,
                                        'subject': subject})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object}
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        course = Course.objects.get(slug=kwargs['slug'])

        if request.user in course.students.all():
            context['is_enrolled'] = True
        else:
            context['is_enrolled'] = False

        context['reviews'] = CourseReview.objects.filter(course=self.object)

        finished_count = FinishedModule.objects.filter(user=request.user, module__course=self.get_object()).count()
        all_modules_count = Module.objects.filter(course=self.object).count()
        if all_modules_count == 0:
            progress = 100
        else:
            progress = int(finished_count / all_modules_count * 100)

        try:
            my_review = get_object_or_404(CourseReview, user=request.user, course=self.object)
        except Http404:
            my_review = None

        if my_review:
            context['my_review'] = my_review
            context['reviews'] = context['reviews'].exclude(id=my_review.id)
        elif progress > 30:
            context['review_form'] = ReviewForm()

        return self.render_to_response(context=context)


class CheckTestView(View):
    """
    View checks if the test form the request is right.
    The difference from CheckTestView is that this view checks the test after user sent a form of a single test.
    """

    def get(self, request, module_id, test_id):
        test = Test.objects.get(id=test_id)
        is_test_right = True
        # ti = test item
        for ti in test.testitem_set.all():
            if ti.right:
                if ('choice_' + str(ti.id)) in request.GET:
                    continue
                else:
                    is_test_right = False
            else:
                if ('choice_' + str(ti.id)) in request.GET:
                    is_test_right = False

        if is_test_right:
            status = "right"
        else:
            status = "wrong"

        try:
            done_test = DoneTest.objects.filter(user=request.user, test=test)[0]
        except IndexError:
            done_test = None

        if done_test is not None:
            if is_test_right:
                done_test.status = "right"
                done_test.save()
            else:
                done_test.status = "wrong"
                done_test.save()
        else:
            DoneTest.objects.create(test=test,
                                    user=request.user,
                                    status=status)

        course_id = Module.objects.get(id=module_id).course.id

        for ti in test.testitem_set.all():
            if ('choice_' + str(ti.id)) in request.GET:
                is_checked = True
            else:
                is_checked = False

            try:
                users_ti = UsersTestItems.objects.filter(test_item=ti)[0]
            except IndexError:
                users_ti = None

            if users_ti is None:
                UsersTestItems.objects.create(user=request.user,
                                              test_item=ti,
                                              is_checked=is_checked)
            else:
                if ('choice_' + str(ti.id)) in request.GET:
                    users_ti.is_checked = True
                else:
                    users_ti.is_checked = False

                users_ti.save()

        return redirect('student_course_detail_module', pk=course_id, module_id=module_id)


class ProcessModuleFinishedView(View):
    def get(self, request, module_id):
        module_tests = get_tests_for_module(module_id)
        users_passed_tests = [t.test for t in DoneTest.objects.filter(user=request.user, status="right")]
        is_finished = True

        for t in module_tests:
            if t in users_passed_tests:
                continue
            else:
                is_finished = False

        if is_finished:
            try:
                f_module = FinishedModule.objects.filter(user=request.user, module_id=module_id)[0]
            except IndexError:
                f_module = None
            print(f_module)
            if f_module is None:
                FinishedModule.objects.create(user=request.user,
                                              module=Module.objects.get(id=module_id))

        return HttpResponse(status=200)


class CheckTestWasDoneView(View):
    """
    View checks if the test form the request is right.
    The difference from CheckTestView is that this view checks the test in order to
    define statuses of all tests from a page.
    """

    def get(self, request, test_id):
        test = Test.objects.get(id=test_id)
        answers = {}
        for users_test_item in UsersTestItems.objects.filter(user=request.user).filter(test_item__test=test):
            if users_test_item.is_checked:
                answers['choice_' + str(users_test_item.test_item.id)] = True
            else:
                answers['choice_' + str(users_test_item.test_item.id)] = False

        done_tests = [passed_test.test for passed_test in DoneTest.objects.filter(user=request.user)]
        status = test.donetest_set.filter(user=request.user)[0].status
        if test in done_tests:
            return HttpResponse(json.dumps({'status': f'{status}', 'answers': answers}))

        return HttpResponse(json.dumps({'status': 'not_done'}))


class CheckModuleFinishedView(View):
    def get(self, request, module_id):
        try:
            f_module = FinishedModule.objects.filter(user=request.user, module__id=module_id)[0]
        except IndexError:
            return HttpResponse(json.dumps({'response': False}))

        return HttpResponse(json.dumps({'response': True}))
