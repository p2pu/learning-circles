import logging
import unicodecsv

from django import http
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import gettext as _
from django.utils.translation import get_language
import json
from django.views.decorators.http import require_http_methods
from django.conf import settings

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib import messages

from courses import models as course_model
from courses.forms import CourseCreationForm
from courses.forms import CourseUpdateForm
from courses.forms import CourseTermForm
from courses.forms import CourseImageForm
from courses.forms import CourseStatusForm
from courses.forms import CourseTagsForm
from courses.forms import CourseEmbeddedUrlForm
from courses.decorators import require_organizer
from courses.badges_oembed import add_content_from_response
from courses.badges_oembed import BadgeNotFoundException

from content import models as content_model
from content.forms import ContentForm

from media import models as media_model


log = logging.getLogger(__name__)


def _get_course_or_404( course_uri ):
    try:
        course = course_model.get_course(course_uri)
    except course_model.ResourceNotFoundException as e:
        raise http.Http404
    return course


def _populate_course_context( request, course_id, context ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    course['author'] = course['author_uri'].strip('/').split('/')[-1]
    context['course'] = course
    context['course_url'] = reverse('courses_show',
        kwargs={'course_id': course['id'], 'slug': course['slug']}
    )
    if 'image_uri' in course:
        context['course']['image'] = media_model.get_image(course['image_uri'])

    user_uri = u"/uri/user/{0}".format(request.user.username)
    context['organizer'] = course_model.is_organizer(course_uri, user_uri)
    context['organizer'] |= request.user.is_superuser
    context['admin'] = request.user.is_superuser
    context['can_edit'] = context['organizer'] and not course['status'] == 'archived'
    context['trusted_user'] = request.user.has_perm('users.trusted_user')

    if 'based_on_uri' in course:
        course['based_on'] = course_model.get_course(course['based_on_uri'])

    return context


@login_required
def create_course( request ):
    if request.method == "POST":
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            user = request.user
            user_uri = u"/uri/user/{0}".format(user.username)
            course = {
                'title': form.cleaned_data.get('title'),
                'hashtag': form.cleaned_data.get('hashtag'),
                'description': form.cleaned_data.get('description'),
                'language': form.cleaned_data.get('language'),
                'organizer_uri': user_uri
            }
            course = course_model.create_course(**course)
            redirect_url = reverse('courses_show', 
                kwargs={'course_id': course['id'], 'slug': course['slug']}
            )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = CourseCreationForm(initial={'language': get_language()})

    context = { 'form': form }
    return render(request, 'courses/create_course.html', context)


@require_organizer
def clone_course( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    user_uri = u"/uri/user/{0}".format(request.user.username)
    course = course_model.clone_course(course_uri, user_uri)
    return course_slug_redirect(request, course['id'])


def course_slug_redirect( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    redirect_url = reverse('courses_show', 
        kwargs={'course_id': course_id, 'slug': course['slug']})
    return http.HttpResponseRedirect(redirect_url)


def show_course( request, course_id, slug=None ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    
    if slug != course['slug']:
        return course_slug_redirect( request, course_id)

    context = { }
    context = _populate_course_context(request, course_id, context)
    context['about_active'] = True

    if context['organizer']:
        context['update_form'] = CourseUpdateForm(course)

    context['about'] = content_model.get_content(course['about_uri'])

    return render(request, 'courses/course.html', context)


@login_required
@require_organizer
def course_admin_content( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
 
    context = { }
    context = _populate_course_context(request, course_id, context)
    context['content_active'] = True

    return render(
        request,
        'courses/course_admin_content.html',
        context
    )


@login_required
@require_organizer
def course_settings( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
 
    context = { }
    context = _populate_course_context(request, course_id, context)

    context['update_form'] = CourseUpdateForm(course)
    context['image_form'] = CourseImageForm()
    context['status_form'] = CourseStatusForm(course)
    tags = ", ".join(course_model.get_course_tags(course_uri))
    context['tags_form'] = CourseTagsForm({'tags': tags})
    context['settings_active'] = True

    return render(
        request,
        'courses/course_settings.html',
        context
    )


@login_required
@require_http_methods(['POST'])
@require_organizer
def course_image( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    user_uri = u"/uri/user/{0}".format(request.user.username)
    image_form = CourseImageForm(request.POST, request.FILES)
    if image_form.is_valid():
        image_file = request.FILES['image']
        image = media_model.upload_image(image_file, course_uri)
        course_model.update_course(
            course_uri=course_uri,
            image_uri=image['uri'],
        )
    else:
        messages.error(request, _("Could not upload image"))
    redirect_url = reverse('courses_settings', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_organizer
def course_content_image_upload( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    user_uri = u"/uri/user/{0}".format(request.user.username)
    if request.method == 'POST':
        image_form = CourseImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image_file = request.FILES['image']
            image = media_model.upload_image(image_file, course_uri)
            if request.headers.get('accept') == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return http.JsonResponse({
                    'status': 'success',
                    'image_uri': image['uri'],
                    'image_url': image['url'],
                })
            redirect_url = reverse('courses_show',
                kwargs={'course_id': course_id, 'slug': 'ermm'}
            )

            return http.HttpResponseRedirect(redirect_url)
        else:
            messages.error(request, _("Could not upload image"))
    else:
        image_form = CourseImageForm()
 
    context = _populate_course_context(request, course_id, {})
    context["form"] = image_form

    return render(
        request,
        'courses/content_image_form.html',
        context
    )


@login_required
@require_http_methods(['POST'])
@require_organizer
def course_change_status( request, course_id ):
    user_uri = u"/uri/user/{0}".format(request.user.username)
    course_uri = course_model.course_id2uri(course_id)
    form = CourseStatusForm(request.POST)
    if form.is_valid():
        status = form.cleaned_data['status']
        if status == 'draft':
            course = course_model.unpublish_course(course_uri)
        elif status == 'published':
            course = course_model.publish_course(course_uri)
        elif status == 'archived':
            course = course_model.archive_course(course_uri)
        messages.success(request, _('Course status updated.'))

    redirect_url = reverse('courses_settings', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_http_methods(['POST'])
@require_organizer
def course_update_attribute( request, course_id, attribute):
    course_uri = course_model.course_id2uri(course_id)
    form = CourseUpdateForm(request.POST)
    if form.is_valid():
        kwargs = { attribute: form.cleaned_data[attribute] }
        course_model.update_course( course_uri, **kwargs )
    else:
        messages.error(request, _("Could not update {0}.".format(attribute)))
    redirect_url = reverse('courses_settings', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_http_methods(['POST'])
@require_organizer
def course_update_tags( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    form = CourseTagsForm(request.POST)
    if form.is_valid():
        tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
        course_model.remove_course_tags(
            course_uri, course_model.get_course_tags(course_uri)
        )
        course_model.add_course_tags(course_uri, tags)
        messages.success( request, _("Course tags successfully updated") )

    redirect_url = reverse('courses_settings', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


def show_content( request, course_id, content_id):
    content_uri = u'/uri/content/{0}'.format(content_id)
    user_uri = u"/uri/user/{0}".format(request.user.username)
    context = _populate_course_context(request, course_id, {})

    if not any( c['uri'] == content_uri for c in context['course']['content']):
       raise http.Http404

    content = content_model.get_content(content_uri)
    context['content'] = content
    context['content_active'] = True

    context['form'] = ContentForm(content)
    return render(
        request,
        'courses/content.html', 
        context
    )


@login_required
@require_organizer
def create_content( request, course_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            user = request.user
            user_uri = u"/uri/user/{0}".format(user.username)
            content_data = {
                'title': form.cleaned_data.get('title'),
                'content': form.cleaned_data.get('content'),
                'author_uri': user_uri,
            }
            content = content_model.create_content(**content_data)
            course_model.add_course_content(course['uri'], content['uri'])

            redirect_url = request.POST.get('next_url', None)
            if not redirect_url:
                redirect_url = reverse('courses_show',
                    kwargs={'course_id': course['id'], 'slug': course['slug']}
                )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm()

    context = { 'form': form }
    context = _populate_course_context(request, course_id, context)
    if request.GET.get('next_url', None):
        context['next_url'] = request.GET.get('next_url', None)

    return render(
        request,
        'courses/create_content.html', 
        context
    )


@login_required
@require_organizer
def edit_content( request, course_id, content_id ):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    content = content_model.get_content("/uri/content/{0}".format(content_id))

    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            content_data = {
                'title': form.cleaned_data.get('title'),
                'content': form.cleaned_data.get('content'),
            }
            user = request.user
            user_uri = u"/uri/user/{0}".format(user.username)
            content = content_model.update_content(
                content['uri'], content_data['title'], 
                content_data['content'], user_uri
            )
            
            redirect_url = request.POST.get('next_url', None)
            if not redirect_url:
                redirect_url = reverse('courses_content_show',
                    kwargs={'course_id': course_id, 'content_id': content_id}
                )
            return http.HttpResponseRedirect(redirect_url)
    else:
        form = ContentForm(initial=content)

    context = {
        'form': form,
        'content': content,
    }
    context = _populate_course_context(request, course_id, context)
    if request.GET.get('next_url', None):
        context['next_url'] = request.GET.get('next_url', None)
    return render(
        request,
        'courses/edit_content.html', 
        context
    )


@login_required
@require_http_methods(['POST'])
def preview_content( request ):
    content = request.POST.get('content')
    from content import utils
    content = utils.clean_user_content(content)
    content = render_to_string("courses/preview_content_snip.html", 
        {'content':content })
    return http.HttpResponse(content, mimetype="application/json")


@login_required
@require_organizer
def remove_content( request, course_id, content_id ):
    course_uri = course_model.course_id2uri(course_id)
    content_uri = "/uri/content/{0}".format(content_id)
    course_model.remove_course_content(course_uri, content_uri)
    redirect_url = reverse('courses_admin_content', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_organizer
def move_content_up( request, course_id, content_id ):
    try:
        course_model.reorder_course_content(
            "/uri/content/{0}".format(content_id), "UP"
        )
    except:
        messages.error(request, _("Could not move content up!"))
    redirect_url = reverse('courses_admin_content', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_organizer
def move_content_down( request, course_id, content_id ):
    try:
        course_model.reorder_course_content(
            "/uri/content/{0}".format(content_id), "DOWN"
        )
    except:
        messages.error(request, _("Could not move content down!"))
    redirect_url = reverse('courses_admin_content', kwargs={'course_id': course_id})
    return http.HttpResponseRedirect(redirect_url)


@login_required
@require_organizer
def delete_spam(request, course_id):
    course_uri = course_model.course_id2uri(course_id)
    course = _get_course_or_404(course_uri)
    if request.method == "POST":
        course_model.delete_spam_course(course_uri)
        #TODO display splash message to indicate success
        return http.HttpResponseRedirect(reverse('home'))

    context = { }
    context = _populate_course_context(request, course_id, context)
    return render(
        request,
        'courses/course_delete_confirmation.html', 
        context
    )
