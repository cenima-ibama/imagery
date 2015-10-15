# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from .views import SceneListView, SceneDetailView, cloud_rate_view, login_view, logout_view, scheduling_view


urlpatterns = patterns('',
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
    url(r'^cloud-rate/$', cloud_rate_view, name='cloud-rate'),
    url(r'^scheduling/$', login_required(scheduling_view, login_url='/login/'), name='scheduling')
)
