from django.conf.urls import *

from splango import views


urlpatterns = patterns(
    url(r'^confirm_human/$', views.confirm_human, name="splango_confirm_human"),

    url(r'^admin/$',
        views.experiments_overview,
        name="splango_admin"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/$',
        views.experiment_detail,
        name="splango_experiment_detail"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<report_id>\d+)/$',
        views.experiment_report,
        name="splango_experiment_report"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<variant>[^/]+)/(?P<goal>[^/]+)/$',
        views.experiment_log,
        name="splango_experiment_log"),
)
