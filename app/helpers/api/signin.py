import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config

class SigninApp:

    @classmethod
    async def signin(cls, email, password):
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            timeout = httpx.Timeout(20.0, connect=10.0)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
                response = await client.post(url=config.API_URL, headers=config.HEADERS, params={"page": "signin"},json={"email": email})
                if not response.is_success:
                    DataFormatter.log_msg(f"{response.status_code}", tag="signin_error")
                    return None
                result = response.json()
                if result.get("status") != "success":
                    DataFormatter.log_msg("invalid user", tag="signin_error")
                    return None
                user = result.get("data")
                if not user:
                    return None
                api_password = str(user.get("password", "")).strip()
                input_password = str(password).strip()
                if not DataFormatter.password_bcrypt(input_password, api_password):
                    DataFormatter.log_msg("invalid password", tag="signin_error")
                    return None
                res_token = await client.post(url=config.API_URL, headers=config.HEADERS, params={"page": "gettoken"}, json={"user": user})
                if res_token.is_success:
                    token_data = res_token.json()
                    if token_data.get("status") == "success":
                        user.pop("password", None)
                        user["token"] = token_data.get("token")
                        return user
                    else:
                        DataFormatter.log_msg("failed token generate in server!", tag="signin_error")
                        return None
                else:
                    DataFormatter.log_msg("failed call endpoint api", tag="signin_error")
                    return None
        except Exception as err:
            DataFormatter.log_msg(f"internal server error: {err}", tag="signin_error")
            raise err