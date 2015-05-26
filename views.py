from django.views.generic import ListView

from .models import Scene


class SceneListView(ListView):
    model = Scene
    context_object_name = 'scenes'
    paginate_by = 20