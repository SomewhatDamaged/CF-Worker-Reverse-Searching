from urllib.parse import urlsplit, parse_qs, urlparse
from workers import WorkerEntrypoint, Response, Request
import traceback
from json import dumps, loads
from typing import Union
from js import fetch as pyfetch

class Default(WorkerEntrypoint):
    json_header = {"content-type": "application/json;charset=UTF-8"}
    async def fetch(self, request: Request) -> Response:
        try:
            url = urlparse(request.url)
            pathname = url.path
            # raise ValueError(f"url.pathname: {pathname}")
            pathname = pathname[7:]
            if request.method == "GET":
                if pathname.startswith("/hashcompare"):
                    return await self.hashcompare(request)
                if pathname.startswith("/hashlist"):
                    return await self.hashlist(request)
                if pathname.startswith("/scamscore"):
                    return await self.scamscore(request)
            if request.method == "POST":
                if pathname.startswith("/fluffle"):
                    return await self.fluffle(request)
                if pathname.startswith("/ocr") and False: # This endpoint currently disabled.
                    return await self.ocr(request)
            return Response(status=404)
        except Exception:
            headers = {"content-type": "text/plain;charset=UTF-8"}
            return Response(f"Traceback: {traceback.format_exc()}", headers=headers, status=500)


    async def fluffle(self, request: Request) -> Response:
        url = urlsplit(request.url)
        queries = parse_qs(url.query)
        if "url" not in queries.keys():
            return Response('{"error": "Missing \'url\' parameter"}', headers=self.json_header, status=400)
        return Response(f"great success: {url}", headers={"content-type": "text/plain;charset=UTF-8"}, status=200)