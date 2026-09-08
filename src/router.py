from fluffle import fluffle
from urllib.parse import urlsplit, parse_qs, urlparse
from workers import WorkerEntrypoint, Response, Request
import traceback

class Default(WorkerEntrypoint):
    async def fetch(self, request: Request) -> Response:
        try:
            url = urlparse(request.url)
            pathname = url.path
            # raise ValueError(f"url.pathname: {pathname}")
            pathname = pathname[self.env.PATH_DEPTH:]
            if request.method == "GET":
                if pathname.startswith("/hashcompare"):
                    return await self.hashcompare(request)
                # ...
            if request.method == "POST":
                if pathname.startswith("/fluffle"):
                    return await fluffle(request)
                # ...
            return Response(status=404)
        except Exception:
            headers = {"content-type": "text/plain;charset=UTF-8"}
            return Response(f"Traceback: {traceback.format_exc()}", headers=headers, status=500)


