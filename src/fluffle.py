from urllib.parse import urlsplit, parse_qs
from js import fetch as pyfetch
from workers import Response, Request
import json
import io
from defs import *

async def fluffle(request: Request) -> Response:
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
    response = await pyfetch("https://api.fluffle.xyz/exact-search-by-file", {"method": "POST"}, headers=headers,
                             files=files, data=data)
    response = await response.json()
    response = response.to_py()
    result = {
        "success": True,
        "data": response
    }
    return Response(json.dumps(result), headers=json_header, status=200)