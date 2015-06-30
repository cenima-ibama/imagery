# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import SceneListView, SearchView, SceneDetailView, cloud_rate_view


urlpatterns = patterns('',
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^search/$', SearchView.as_view(), name='search'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
    url(r'^cloud-rate/$',
        cloud_rate_view,
        name='cloud-rate'
        ),
)