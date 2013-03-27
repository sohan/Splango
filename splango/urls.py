from django.conf.urls import patterns, include, url

from splango import views


urlpatterns = patterns(
    '',
    url(r'^admin/$',
        views.experiments_overview,
        name="splango_admin"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/$',
        views.experiment_detail,
        name="splango_experiment_detail"),
    url(r'^admin/exp/report/(?P<report_id>\d+)/$',
        views.experiment_report,
        name="splango_experiment_report"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<variant>[^/]+)/(?P<goal>[^/]+)/$',
        views.experiment_log,
        name="splango_experiment_log"),
    url(r'^admin/goal/report/(?P<goal_name>[^/]+)/(?P<exp_name>[^/]+)/$',
        views.experiment_goal_report,
        name="splango_experiment_goal_report"),

)
