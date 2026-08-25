import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config


class InfoApp:

    @classmethod
    async def info_app(cls):
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            timeout = httpx.Timeout(20.0, connect=10.0)
            query_params = {"page": "infoserver"}
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
                response = await client.get(url=config.API_URL, headers=config.HEADERS, params=query_params)
                if response.is_success:
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        result = response.json()
                        return result.get("data", [])
                    else:
                        DataFormatter.log_msg(f"response is not json: {response.text[:100]}", tag="appinfo_error")
                        return None
                else:
                    DataFormatter.log_msg(f"http error: {response.status_code}", tag="appinfo_error")
                    return None
        except httpx.TimeoutException:
            DataFormatter.log_msg("request timeout", tag="appinfo_error")
            return None
        except Exception as err:
            DataFormatter.log_msg(f"internal server error: {err}", tag="appinfo_error")
            return None