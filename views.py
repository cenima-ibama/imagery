from rest_framework.generics import RetrieveAPIView

from datetime import date, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, DeleteView
from django.template import RequestContext
from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Avg
from django.utils.translation import ugettext, ugettext_lazy as _

from .forms import SceneRequestForm
from .models import Scene, SceneRequest
from .serializers import SceneSerializer
from .utils import three_digit


class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super(SceneListView, self).get_queryset()

        self.name = self.request.GET.get('name', None)
        self.path = self.request.GET.get('path', None)
        self.row = self.request.GET.get('row', None)
        self.status = self.request.GET.get('status', None)
        self.sat = self.request.GET.get('sat', None)
        self.start = self.request.GET.get('start', None)
        self.end = self.request.GET.get('end', None)
        self.max_cloud = self.request.GET.get('max_cloud', 100)

        if self.name:
            queryset = queryset.filter(name__icontains=self.name)
        if self.path:
            queryset = queryset.filter(path=three_digit(self.path))
        if self.row:
            queryset = queryset.filter(row=three_digit(self.row))
        if self.status:
            queryset = queryset.filter(status=self.status)
        if self.sat:
            queryset = queryset.filter(sat=self.sat)
        if self.start:
            queryset = queryset.filter(date__gte=self.start)
        if self.end:
            queryset = queryset.filter(date__lte=self.end)
        if self.max_cloud:
            queryset = queryset.filter(cloud_rate__lte=self.max_cloud)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SceneListView, self).get_context_data(**kwargs)

        if self.name:
            context['name'] = self.name
        if self.path:
            context['path'] = self.path
        if self.row:
            context['row'] = self.row
        if self.status:
            context['status'] = self.status
        if self.sat:
            context['sat'] = self.sat
        if self.start:
            context['start'] = self.start
        if self.end:
            context['end'] = self.end
        if self.max_cloud:
            context['max_cloud'] = self.max_cloud

        queries_without_page = self.request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']

        context['queries'] = queries_without_page

        return context


class SceneDetailView(DetailView):
    model = Scene
    context_object_name = 'scene'
    slug_field = 'name'


class GeoSceneDetailView(RetrieveAPIView):
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer
    lookup_field = 'name'


def cloud_rate_view(request):
    days = [date.today() - timedelta(days=i) for i in range(1, 17)]
    rates = [Scene.objects.filter(date=day).aggregate(Avg('cloud_rate')).get('cloud_rate__avg') for day in days]
    data = zip(days, rates)

    return render(request, 'imagery/cloud_rate.html', {'cloud_rate_data': data})


def login_view(request):
    context = RequestContext(request)
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('imagery:index'))
            else:
                msg = _('Your account is not active, Please contact the system administrator')
                return render_to_response(
                    'imagery/login_user.html',
                    {'msg': msg}, context_instance=context
                )
        else:
            msg = _('Invalid username or password')
            return render_to_response(
                'imagery/login_page.html',
                {'msg': msg}, context_instance=context
            )
    else:
        return render_to_response('imagery/login_page.html',
            context_instance=context)


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect(reverse('imagery:index'))


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, login_url='imagery:login')


def request_scene_view(request):
    context = RequestContext(request)
    if request.POST:
        form = SceneRequestForm(request.POST)
        if form.is_valid():
            scene_request = SceneRequest(
                scene_name=request.POST.get('scene_name'),
                user=request.user
            )
            scene_request.save()
            form = SceneRequestForm()
            return render_to_response(
                'imagery/request_scene.html',
                {'msg': _('Scene %s was scheduled to download.' % scene_request.scene_name),
                    'form': form},
                context_instance=context
            )
    else:
        form = SceneRequestForm()
    return render_to_response(
        'imagery/request_scene.html',
        {'form': form},
        context_instance=context
    )


class SceneRequestListView(ListView):
    """Base view to all SceneRequestListViews."""
    model = SceneRequest
    context_object_name = 'scenes'


class SceneRequestByUserListView(SceneRequestListView):
    """List Scene Requests by User."""
    template_name = 'imagery/user_scenerequest_list.html'

    def get_queryset(self):
        return SceneRequest.objects.filter(user=self.request.user)


class NotFoundSceneRequestListView(SceneRequestListView):
    """List Scene Requests that were not found on AWS or Google Earth Engine
    Servers.
    """
    template_name = 'imagery/not_found_scenerequest.html'

    def get_queryset(self):
        return SceneRequest.objects.filter(status='not_found')


class SceneRequestDeleteView(LoginRequiredMixin, DeleteView):
    """Delete SceneRequest objects. Only the user that created the SceneRequest
    can delete it.
    """
    model = SceneRequest
    context_object_name = 'scenerequest'
    success_url = reverse_lazy('imagery:user-scene-request')

    def get_queryset(self):
        qs = super(SceneRequestDeleteView, self).get_queryset()
        return qs.filter(user=self.request.user)