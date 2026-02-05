from django.urls import re_path

from courses import views

urlpatterns = [
    re_path(r'^create/$', views.create_course,
        name='courses_create'),

    re_path(r'^(?P<course_id>[\d]+)/clone/$',
        views.clone_course,
        name='courses_clone'),

    re_path(r'^(?P<course_id>[\d]+)/$',
        views.course_slug_redirect,
        name='courses_slug_redirect'),

    re_path(r'^(?P<course_id>[\d]+)/admin_content/$',
        views.course_admin_content,
        name='courses_admin_content'),

    re_path(r'^(?P<course_id>[\d]+)/settings/$',
        views.course_settings,
        name='courses_settings'),

    re_path(r'^(?P<course_id>[\d]+)/delete_spam/$',
        views.delete_spam,
        name='courses_delete_spam'),

    re_path(r'^(?P<course_id>[\d]+)/upload_image/$',
        views.course_image,
        name='courses_image'),

    # view to upload image for content
    re_path(
        r'^(?P<course_id>[\d]+)/content/upload_image/$',
        views.course_content_image_upload,
        name='courses_content_image_upload'
    ),

    re_path(r'^(?P<course_id>[\d]+)/change_status/$',
        views.course_change_status,
        name='courses_change_status'),

    re_path(r'^(?P<course_id>[\d]+)/update/(?P<attribute>[\w_]+)/$',
        views.course_update_attribute,
        name='courses_update_attribute'),

    re_path(r'^(?P<course_id>[\d]+)/update_tags/$',
        views.course_update_tags,
        name='courses_update_tags'),

    re_path(r'^(?P<course_id>[\d]+)/(?P<slug>[\w-]+)/$',
        views.show_course,
        name='courses_show'),

    re_path(r'^(?P<course_id>[\d]+)/content/create/$',
        views.create_content,
        name='courses_create_content'),

    re_path(r'content/preview/$',
        views.preview_content,
        name='courses_preview_content'),

    re_path(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/$',
        views.show_content,
        name='courses_content_show'),
    
    re_path(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/edit/$',
        views.edit_content,
        name='courses_content_edit'),

    re_path(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/remove/$',
        views.remove_content,
        name='courses_content_remove'),

    re_path(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/up/$',
        views.move_content_up,
        name='courses_content_up'),

    re_path(r'^(?P<course_id>[\d]+)/content/(?P<content_id>[\d]+)/down/$',
        views.move_content_down,
        name='courses_content_down'),
]
