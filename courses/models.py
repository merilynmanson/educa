from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string

from .fields import OrderField


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User,
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,
                            unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User,
                                      related_name='courses',
                                      blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': (
                                         'text',
                                         'video',
                                         'image',
                                         'file',
                                         'test')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        i = -1  # Set -1 because we need to start since zero-ID
        module_items = []
        while not self in module_items:
            i += 1
            module_items = [x.item for x in Content.objects.filter(module__id=i)]

        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self,
             'module': Module.objects.get(id=i)}
        )


class Text(ItemBase):
    content = models.TextField()


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Video(ItemBase):
    url = models.URLField()


class Test(ItemBase):
    title = models.CharField(max_length=500)


class TestItem(models.Model):
    right = models.BooleanField()
    item_title = models.CharField(max_length=150)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)


class FinishedModule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)


class DoneTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    # Statuses: not_done, right, wrong
    status = models.CharField(max_length=15)


class UsersTestItems(models.Model):
    test_item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_checked = models.BooleanField()
