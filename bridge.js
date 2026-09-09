import { WorkerEntrypoint } from "cloudflare:workers";

// Export the search function directly
export class RpcService extends WorkerEntrypoint {

  async search(imageBytes, limit, contentType) {
    const bytes = new Uint8Array(imageBytes.buffer || imageBytes);
    const host = "api.fluffle.xyz";
    const formData = new FormData();
    const imageBlob = new Blob([bytes], { type: contentType });
    formData.append("file", imageBlob, "image");
    formData.append("limit", String(limit));
    const response = await fetch(`https://${host}/exact-search-by-file`, {
      method: "POST",
      headers: {
        "User-Agent": "ExcessiveSpaceSearcher/1.0 (by dev at excessive space)",
      },
      body: formData
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API returned status ${response.status}: ${errorText}`);
    }
    return await response.json();
  }
}