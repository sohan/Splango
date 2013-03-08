from django.shortcuts import render_to_response
from django.template import RequestContext


def sample(request):
    return render_to_response("sample.html", {}, RequestContext(request))
