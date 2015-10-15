from datetime import date, timedelta

from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView
from django.template import RequestContext
from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.utils.translation import ugettext, ugettext_lazy as _

from .forms import SchedulingForm
from .models import Scene, PastSceneDownload
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
                'imagery/login_user.html',
                {'msg': msg}, context_instance=context
            )
    else:
        return render_to_response('imagery/login_user.html',
            context_instance=context)


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect(reverse('imagery:index'))


def scheduling_view(request):
    context = RequestContext(request)
    if request.POST:
        form = SchedulingForm(request.POST)
        if form.is_valid:
            model = PastSceneDownload(
                scene=request.POST.get('scene'),
                user=request.user
            )
            model.save()
            form = SchedulingForm()
            return render_to_response(
                'imagery/scheduling.html',
                {'msg': _('Download scene %s scheduled' % model.scene), 'form': form},
                context_instance=context
            )
    else:
        form = SchedulingForm()
    return render_to_response(
        'imagery/scheduling.html',
        {'form': form},
        context_instance=context
    )
