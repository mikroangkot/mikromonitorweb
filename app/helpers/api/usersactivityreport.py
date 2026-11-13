import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.supabase import supabase

class SupabaseQueryError(Exception):
	pass

class UsersActivityReport:

	@retry(
		stop=stop_after_attempt(3),
		wait=wait_exponential(multiplier=1, min=2, max=6),
		retry=retry_if_exception_type((Exception, SupabaseQueryError)),
		reraise=True
	)

	@staticmethod
	async def _execute_query(search_term: str = ''):
		def _fetch():
			response = supabase.rpc('get_users_activity_report', {'search_query': search_term}).execute()
			return response.data
		try:
			result = await asyncio.to_thread(_fetch)
			return result
		except Exception as err:
			DataFormatter.log_msg(f'Database query error, retrying...: {err}', tag='usersactivityreport_error')
			raise SupabaseQueryError(f'Gagal mengambil data dari database: {err}')

	@staticmethod
	async def usersactivityreport():
		try:
			result = await UsersActivityReport._execute_query()
			return result if result is not None else []
		except SupabaseQueryError as err:
			DataFormatter.log_msg(f"failed data: {err}", tag="usersactivityreport_error")
			return []
		except Exception as err:
			DataFormatter.log_msg(f"internal server error: {err}", tag="usersactivityreport_error")
			return []