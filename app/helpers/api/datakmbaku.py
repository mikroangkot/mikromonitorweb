import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config

class NonJsonResponseError(Exception):
	pass

class DataKmBaku:

	@classmethod
	@retry(
		stop=stop_after_attempt(3),
		wait=wait_exponential(multiplier=1, min=2, max=6),
		retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException, NonJsonResponseError)),
		reraise=True
	)

	async def _execute_request(cls, token: str):
		query_params = {"page": "datakmbaku"}
		payload = {"token": token}
		timeout = httpx.Timeout(20.0, connect=10.0)
		async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
			response = await client.post(url=config.API_URL, headers=config.HEADERS, params=query_params, json=payload)
			response.raise_for_status()
			content_type = response.headers.get("content-type", "")
			if "application/json" not in content_type:
				DataFormatter.log_msg(f"response is not json, retrying...({response.text[:100]})", tag="datakmbaku_error")
				raise NonJsonResponseError("server response is not json")
			try:
				return response.json()
			except Exception as err:
				raise NonJsonResponseError(f"failed parse json: {err}")

	@classmethod
	async def datakmbaku(cls):
		storage = DataFormatter()
		try:
			token = await storage.get("token")
			result = await cls._execute_request(token)
			return result.get("data", [])
		except httpx.TimeoutException:
			DataFormatter.log_msg("request timeout", tag="datakmbaku_error")
			return None
		except NonJsonResponseError as err:
			DataFormatter.log_msg(f"failed parse json data: {err}", tag="datakmbaku_error")
			return None
		except Exception as err:
			DataFormatter.log_msg(f"internal server error: {err}", tag="datakmbaku_error")
			return None