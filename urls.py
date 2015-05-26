# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import SceneListView, SceneDetailView


urlpatterns = patterns('',
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
)