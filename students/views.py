from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, FormView, ListView, DetailView

from communicate.forms import CommentForm
from courses.models import Course, FinishedModule, Module, Test, Content
from students.forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if 'module_id' in self.kwargs:
            context['module'] = self.object.modules.get(
                id=self.kwargs['module_id']
            )
        else:
            context['module'] = self.object.modules.all()[0]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        finished_count = FinishedModule.objects.filter(user=request.user, module__course=self.get_object()).count()
        all_modules_count = Module.objects.filter(course=self.object).count()

        if 'module_id' not in kwargs:
            return HttpResponseRedirect(reverse_lazy('student_course_detail_module',
                                                     args=[context['module'].course.id, context['module'].id]))

        if all_modules_count == 0:
            context['progress'] = 100
        else:
            context['progress'] = int(finished_count / all_modules_count * 100)

        context['new_comment_form'] = CommentForm()

        return self.render_to_response(context=context)
