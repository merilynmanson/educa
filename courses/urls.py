from django.urls import path

from courses import views

urlpatterns = [
    path('mine/',
         views.ManageCourseListView.as_view(),
         name='manage_course_list'),
    path('create/',
         views.CourseCreateView.as_view(),
         name='course_create'),
    path('<pk>/edit/',
         views.CourseUpdateView.as_view(),
         name='course_edit'),
    path('<pk>/delete/',
         views.CourseDeleteView.as_view(),
         name='course_delete'),
    path('<pk>/module/',
         views.CourseModuleUpdateView.as_view(),
         name='course_module_update'),
    path('module/<int:module_id>/content/test/create/',
         views.TestCreateUpdateView.as_view(),
         name='module_content_test_create'),
    path('module/<int:module_id>/content/test/<id>/',
         views.TestCreateUpdateView.as_view(),
         name='module_content_test_update'),
    path('module/<int:module_id>/content/<model_name>/create/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_create'),
    path('module/<int:module_id>/content/<model_name>/<id>/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_update'),
    path('content/<int:id>/delete/',
         views.ContentDeleteView.as_view(),
         name='module_content_delete'),
    path('module/<int:module_id>/',
         views.ModuleContentListView.as_view(),
         name='module_content_list'),
    path('module/order/',
         views.ModuleOrderView.as_view(),
         name='module_order'),
    path('content/order/',
         views.ContentOrderView.as_view(),
         name='content_order'),
    path('subject/<slug:subject>/',
         views.CourseListView.as_view(),
         name='course_list_subject'),
    path('<slug:slug>/',
         views.CourseDetailView.as_view(),
         name='course_detail'),
    path('module/<int:module_id>/test/<int:test_id>/check/',
         views.CheckTestView.as_view(),
         name='check_test'),
    path('module/<int:module_id>/process_finished/',
         views.ProcessModuleFinishedView.as_view(),
         name='process_module_finished'),
    path('check_test_was_done/<int:test_id>/',
         views.CheckTestWasDoneView.as_view(),
         name='check_test_was_done'),
    path('module/<int:module_id>/check_finished/',
         views.CheckModuleFinishedView.as_view(),
         name='check_module_finished'),
]
