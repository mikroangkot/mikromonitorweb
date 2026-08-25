import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config


class InfoApp:

    @classmethod
    async def info_app(cls):
        try:
            timeout = httpx.Timeout(10.0, connect=5.0)
            query_params = {"page": "infoserver"}
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=timeout
            ) as client:
                response = await client.get(
                    url=config.API_URL, headers=config.HEADERS, params=query_params
                )
                if response.is_success:
                    try:
                        result = response.json()
                        return result.get("data", [])
                    except ValueError:
                        DataFormatter.log_msg(
                            "error server response", tag="appinfo_error"
                        )
                        return None
                else:
                    DataFormatter.log_msg(
                        f"http error: {response.status_code}", tag="appinfo_error"
                    )
                    return None
        except Exception as err:
            DataFormatter.log_msg(f"{err}", tag="infoapp_error")
            return None
