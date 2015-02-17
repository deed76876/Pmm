from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from accounts import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.accounts,
        name='accounts'),

    url(
        r'^update/$',
        login_required(views.UserUpdateView.as_view()),
        name='accounts_update'),

    url(
        r'^login/$',
        views.login,
        name='login'),
    url(
        r'^oauth2/$',
        views.oauth2,
        name='accounts_oauth2'),
    url(
        r'^logout/$',
        views.logout,
        name='logout'),
)
