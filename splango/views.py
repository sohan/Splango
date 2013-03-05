from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import never_cache

from .models import Enrollment, Experiment, ExperimentReport, Goal, GoalRecord


@never_cache
def confirm_human(request):
    request.experiments_manager.confirm_human()
    return HttpResponse(status=204)


@staff_member_required
def experiments_overview(request):
    experiments = Experiment.objects.all()
    reports = ExperimentReport.objects.all()
    reports_by_id = dict()

    for r in reports:
        reports_by_id.setdefault(r.experiment_id, []).append(r)
    for e in experiments:
        e.reports = reports_by_id.get(e.name, [])

    return render_to_response(
        "splango/experiments_overview.html",
        {"title": "Experiments", "experiments": experiments},
        RequestContext(request))


@staff_member_required
def experiment_detail(request, exp_name):
    exp = get_object_or_404(Experiment, name=exp_name)
    reports = ExperimentReport.objects.filter(experiment=exp)

    return render_to_response(
        "splango/experiment_detail.html",
        {"title": exp.name, "exp": exp, "reports": reports},
        RequestContext(request))


@staff_member_required
def experiment_report(request, exp_name, report_id):
    report = get_object_or_404(ExperimentReport, id=report_id,
                               experiment__name=exp_name)
    report_rows = report.generate()

    dictionary = {"title": report.title, "exp": report.experiment,
                  "report": report, "report_rows": report_rows, }
    return render_to_response("splango/experiment_report.html", dictionary,
                              RequestContext(request))


@staff_member_required
def experiment_log(request, exp_name, variant, goal):
    exp = get_object_or_404(Experiment, name=exp_name)
    goal = get_object_or_404(Goal, name=goal)

    enrollments = (
        Enrollment.objects
        .filter(experiment=exp, variant=variant, subject__goals=goal)
        .select_related("subject")[:1000]
    )
    # 1000 limit is just there to keep this page sane

    goal_records = (
        GoalRecord.objects
        .filter(goal=goal, subject__in=[e.subject for e in enrollments])
        .select_related("goal", "subject")
    )

    title = "Experiment Log: variant %s, goal %s" % (variant, goal)
    activities = list(enrollments) + list(goal_records)
    activities.sort(key=lambda x: x.created)

    dictionary = {"exp": exp, "activities": activities, "title": title}
    return render_to_response("splango/experiment_log.html", dictionary,
                              RequestContext(request))
