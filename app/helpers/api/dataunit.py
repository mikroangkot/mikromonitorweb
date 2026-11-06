from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.supabase import supabase

class SupabaseQueryError(Exception):
	pass

class DataUnit:

	@retry(
		stop=stop_after_attempt(3),
		wait=wait_exponential(multiplier=1, min=2, max=6),
		retry=retry_if_exception_type((Exception, SupabaseQueryError)),
		reraise=True
	)

	@staticmethod
	async def _execute_query():
		try:
			response = supabase.table('unit').select('*').execute()
			return response.data
		except Exception as err:
			DataFormatter.log_msg(f'Database query error, retrying...: {err}', tag='unit_error')
			raise SupabaseQueryError(f'Gagal mengambil data dari database: {err}')

	@staticmethod
	async def dataunit():
		try:
			result = await DataUnit._execute_query()
			return result if result is not None else []
		except SupabaseQueryError as err:
			DataFormatter.log_msg(f"failed data: {err}", tag="dataunit_error")
			return None
		except Exception as err:
			DataFormatter.log_msg(f"internal server error: {err}", tag="dataunit_error")
			return None