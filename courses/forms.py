from django.forms import inlineformset_factory
from django import forms

from communicate.models import CourseReview
from courses.models import Course, Module, Test, TestItem

ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title',
                                              'description'],
                                      extra=2,
                                      can_delete=True)


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title']


TestItemsFormSet = inlineformset_factory(Test,
                                         TestItem,
                                         exclude=[''],
                                         extra=4,
                                         can_delete=True)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = CourseReview
        fields = ('text', 'like')
