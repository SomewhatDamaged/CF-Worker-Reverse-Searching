from urllib.parse import urlsplit, parse_qs
import js
from workers import Response, Request
import json
from defs import *
from pyodide.ffi import to_js
from typing import Any

async def fluffle(request: Request, env: Any) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await js.fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type", "image/png")
    blob = await image_data.blob()
    bridge = getattr(js, "bridge")

    js_result = await bridge.search(
        to_js(blob),
        "8",
        content_type
    )

    result = json.loads(js_result.to_py())
    result = {
        "success": True,
        "data": result,
    }
    return Response(json.dumps(result), headers=json_header, status=200)