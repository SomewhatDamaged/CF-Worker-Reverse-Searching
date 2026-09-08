import io
from urllib.parse import urlsplit, parse_qs, urlparse
from workers import WorkerEntrypoint, Response, Request
import traceback
import json
from typing import Union
from js import fetch as pyfetch

class Default(WorkerEntrypoint):
    json_header = {"content-type": "application/json;charset=UTF-8"}
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
                    return await self.fluffle(request)
                # ...
            return Response(status=404)
        except Exception:
            headers = {"content-type": "text/plain;charset=UTF-8"}
            return Response(f"Traceback: {traceback.format_exc()}", headers=headers, status=500)


    async def fluffle(self, request: Request) -> Response:
        url = urlsplit(request.url)
        queries = parse_qs(url.query)
        if "url" not in queries.keys():
            return Response('{"error": "Missing \'url\' parameter"}', headers=self.json_header, status=400)
        image_data = await pyfetch(queries["url"][0])
        blob = await image_data.blob()
        array_buffer = await blob.arrayBuffer()
        python_bytes = array_buffer.to_py().tobytes()
        buffer = io.BytesIO(python_bytes)
        headers = {
            "User-Agent": "Excessive.Space Reverse Searcher/dev@excessive.space/1.0"
        }
        files = {
            "file": buffer.getvalue()
        }
        data = {
            "limit": 8
        }
        response = await pyfetch("https://api.fluffle.xyz/exact-search-by-file", {"method": "POST"}, header=headers, files=files, data=data)
        response = await response.json()
        result = {
            "success": True,
            "data": await response
        }
        return Response(json.dumps(result), headers=self.json_header, status=200)