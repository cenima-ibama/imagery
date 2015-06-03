from datetime import date, timedelta

from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.db.models import Avg

from .models import Scene


class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    paginate_by = 20


class SceneDetailView(DetailView):
    model = Scene
    context_object_name = 'scene'
    slug_field = 'name'


def cloud_rate_view(request):
    days = [date.today() - timedelta(days=i) for i in range(1, 17)]
    rates = [Scene.objects.filter(date=day).aggregate(Avg('cloud_rate')).get('cloud_rate__avg') for day in days]
    data = zip(days, rates)

    return render(request, 'imagery/cloud_rate.html', {'cloud_rate_data': data})