from urllib.parse import urlsplit, parse_qs
import js
from workers import Response, Request
import json
from defs import *
from pyodide.ffi import to_js

async def fluffle(request: Request) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await js.fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type")
    blob = await image_data.blob()
    form_data = js.FormData.new()
    form_data.append("file", blob, "image." + content_type.split("/")[1])
    form_data.append("limit", "8")
    options = {
        "method": "POST",
        "headers": {
            "User-Agent": user_agent
        },
        "body": form_data
    }
    js_response = await js.fetch(url, to_js(options))
    result = json.loads(await js_response.text())
    result = {
        "success": True,
        "data": result,
    }
    return Response(json.dumps(result), headers=json_header, status=200)