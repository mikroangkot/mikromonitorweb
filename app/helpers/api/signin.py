import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config

class SigninApp:

    @staticmethod
    async def signin(email, password):
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            timeout = httpx.Timeout(20.0, connect=10.0)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
                response = await client.post(
                    url=config.API_URL,
                    headers=config.HEADERS,
                    params={"page": "signinuser"},
                    json={"email": email, "password": password}
                )
                if not response.is_success:
                    DataFormatter.log_msg(f"{response.status_code}", tag="signin_error")
                    return None
                result = response.json()
                if result.get("status") != "success":
                    DataFormatter.log_msg("invalid user", tag="signin_error")
                    return None
                return result
        except Exception as err:
            DataFormatter.log_msg(f"internal server error: {err}", tag="signin_error")
            raise err
