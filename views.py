import django_filters

from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework_gis.pagination import GeoJsonPagination

from datetime import date, timedelta

from django.contrib.gis.geos import Polygon
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


class SceneFilter(django_filters.FilterSet):
    start = django_filters.DateFilter(name='date', lookup_type=('gte')) 
    end = django_filters.DateFilter(name='date', lookup_type=('lte'))
    max_cloud = django_filters.MethodFilter()
    bbox = django_filters.MethodFilter()

    class Meta:
        model = Scene
        fields = {
            'name', 'path', 'row', 'status', 'sat',
            'start', 'end', 'bbox', 'max_cloud'
            }

    def filter_bbox(self, queryset, value):
        bbox = [float(coord) for coord in value.split(',')]
        bbox = Polygon((
            bbox[:2],
            [bbox[0], bbox[3]],
            bbox[2:],
            [bbox[2], bbox[1]],
            bbox[:2]
        ))
        return queryset.filter(geom__intersects=bbox)

    def filter_max_cloud(self, queryset, value):
        return queryset.filter(cloud_rate__lte=value)



class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    template_name = 'imagery/scene_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super(SceneListView, self).get_queryset()
        queryset = SceneFilter(self.request.GET, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SceneListView, self).get_context_data(**kwargs)

        if self.request.GET.get('product'):
            context['product'] = self.request.GET.get('product')
        if self.request.GET.get('name'):
            context['name'] = self.request.GET.get('name')
        if self.request.GET.get('path'):
            context['path'] = self.request.GET.get('path')
        if self.request.GET.get('row'):
            context['row'] = self.request.GET.get('row')
        if self.request.GET.get('status'):
            context['status'] = self.request.GET.get('status')
        if self.request.GET.get('sat'):
            context['sat'] = self.request.GET.get('sat')
        if self.request.GET.get('start'):
            context['start'] = self.request.GET.get('start')
        if self.request.GET.get('end'):
            context['end'] = self.request.GET.get('end')
        if self.request.GET.get('max_cloud', 100):
            context['max_cloud'] = self.request.GET.get('max_cloud', 100)
        if self.request.GET.get('bbox'):
            context['bbox'] = self.request.GET.get('bbox')

        queries_without_page = self.request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']

        context['queries'] = queries_without_page

        return context


class GeoPagination(GeoJsonPagination):
    page_size = 20


class GeoSceneListView(ListAPIView):
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer
    geo_field = 'geom'
    pagination_class = GeoPagination

    def get_queryset(self):
        queryset = super(GeoSceneListView, self).get_queryset()
        queryset = SceneFilter(self.request.GET, queryset)
        return queryset


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