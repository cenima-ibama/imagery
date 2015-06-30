from datetime import date, timedelta

from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.db.models import Avg

from .models import Scene


class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    paginate_by = 20


class SearchView(ListView):
    template_name = 'imagery/scene_list.html'

    def get_queryset(self):
        self.name = self.request.GET.get('name', None)
        self.sat = self.request.GET.get('sat', None)
        self.start = self.request.GET.get('start', None)
        self.end = self.request.GET.get('end', None)
        self.min_cloud = self.request.GET.get('min_cloud', None)
        self.max_cloud = self.request.GET.get('max_cloud', None)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        queryset = Scene.objects.all()

        if self.name:
            queryset = queryset.filter(name__icontains=self.name)
        if self.sat:
            queryset = queryset.filter(sat=self.sat)
        if self.start:
            queryset = queryset.filter(date__gte=self.start)
        if self.end:
            queryset = queryset.filter(date__lte=self.end)
        if self.min_cloud:
            queryset = queryset.filter(cloud_rate__gte=self.min_cloud)
        if self.max_cloud:
            queryset = queryset.filter(cloud_rate__lte=self.max_cloud)

        context['scenes'] = queryset

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