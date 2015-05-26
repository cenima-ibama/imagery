from django.views.generic import ListView, DetailView

from .models import Scene


class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    paginate_by = 20


class SceneDetailView(DetailView):
    model = Scene
    context_object_name = 'scene'
    slug_field = 'name'
