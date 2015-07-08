# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import SceneListView, SceneDetailView, cloud_rate_view


urlpatterns = patterns('',
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
    url(r'^cloud-rate/$',
        cloud_rate_view,
        name='cloud-rate'
        ),
    url(r'^resources/$',
        TemplateView.as_view(template_name='imagery/resources.html'),
        name='resources'),
)