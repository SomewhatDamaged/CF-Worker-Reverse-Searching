from urllib.parse import urlsplit, parse_qs
from js import fetch as pyfetch
from workers import Response, Request
import json
import io
from defs import *
import aiohttp

async def fluffle(request: Request) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await pyfetch(queries["url"][0])
    blob = await image_data.blob()
    array_buffer = await blob.arrayBuffer()
    python_bytes = array_buffer.to_py().tobytes()
    buffer = io.BytesIO(python_bytes)
    headers = {
        "User-Agent": "Excessive.Space Reverse Searcher/dev@excessive.space/1.0"
    }
    data = aiohttp.FormData()
    data.add_field("file", buffer.getvalue(), filename="image", content_type="image/*")
    data.add_field("limit", "8", content_type="text/plain")
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.fluffle.xyz/exact-search-by-file', headers=headers, data=data) as response:
            result = await response.json()
    result = {
        "success": True,
        "data": result
    }
    return Response(json.dumps(result), headers=json_header, status=200)