from typing import Union

from fluffle import fluffle
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response, Request
import traceback
from defs import *
from json import loads, dumps

class Default(WorkerEntrypoint):
    async def fetch(self, request: Request) -> Response:
        try:
            url = urlparse(request.url)
            pathname = url.path
            pathname = pathname[self.env.PATH_DEPTH:]
            if request.method == "GET":
                if pathname.startswith("/test"):
                    return Response(status=100)
                # ...
            if request.method == "POST":
                if pathname.startswith("/fluffle"):
                    response = await self.authenticate(request, "reverse")
                    if isinstance(response, Response):
                        return response
                    return await fluffle(request, self.env)
                # ...
            return Response(status=404)
        except Exception:
            data = {
                "traceback": str(traceback.format_exc()),
                "success": False,
            }
            return Response(dumps(data), headers=json_header, status=500)

    async def authenticate(self, request: Request, endpoint_name: str) -> Union[Response,str]:
        headers = dict(request.headers)
        if "authorization" not in headers.keys():
            return Response('{"error": "Missing \'authorization\' parameter", "success": false}', headers=json_header, status=401)
        if not headers["authorization"].startswith("Bearer "):
            return Response('{"error": "Bad \'authorization\' parameter"}', headers=json_header, status=401)
        key = headers["authorization"].split(" ")[1]
        key_data = str(await self.env.KEYS.get(key)).strip()
        if not key_data.startswith("{"):
            return Response('{"error": "Invalid \'key\' parameter"}', headers=json_header, status=401)
        authorized_data = loads(key_data)
        if authorized_data is None:
            return Response('{"error": "Error parsing key data from KV storage"}', headers=json_header, status=500)
        if endpoint_name not in authorized_data["access"]:
            return Response('{"error": "You do not have access to this endpoint"}', headers=json_header, status=403)
        return key