# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import SceneListView

urlpatterns = patterns('',
    url(r'^$', SceneListView.as_view(template_name='scene_list.html'), name='index'),

)