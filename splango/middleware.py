from splango import RequestExperimentManager


class ExperimentsMiddleware:

    def process_request(self, request):
        request.experiments_manager = RequestExperimentManager(request)
        return None

    def process_response(self, request, response):
        if getattr(request, "experiments_manager", None):
            request.experiments_manager.finish(response)
        return response
