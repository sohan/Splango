from splango import RequestExperimentManager


class ExperimentsMiddleware:

    def process_request(self, request):
        """Assign the Experiment Manager to the request."""
        request.experiments_manager = RequestExperimentManager(request)
        return None

    def process_response(self, request, response):
        """Retrieve the Experiment Manager from the request and assign it to
        the response."""
        if getattr(request, "experiments_manager", None):
            request.experiments_manager.finish(response)
        return response
