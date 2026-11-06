import asyncio
from typing import Optional
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config
from app.helpers.utility.supabase import supabase

class UserActivity:

    @staticmethod
    async def useractivity(username: str, last_activity: str) -> bool:
        storage = DataFormatter()
        lokasi = (await storage.get("current_location")) or {}
        ip_address = lokasi.get("ip_address") or "127.0.0.1"
        lat_long = f"https://www.google.com/maps/search/?api=1&query={lokasi.get('latlong') or '0.0,0.0'}"
        query_params = {"page": "useractivity"}
        payload = {
            "app_name": f"{config.APP_NAME} Versi {config.APP_VERSION}",
            "username": username,
            "last_activity": last_activity,
            "ip_address": ip_address,
            "lat_long": lat_long,
        }
        def _insert_supabase() -> Optional[dict]:
            try:
                response = supabase.table('users_activity').insert(payload).execute()
                return response.data[0] if response.data else None
            except Exception as err:
                DataFormatter.log_msg(f'{err}', tag='supabase_error')
                return None
        record = await asyncio.to_thread(_insert_supabase)
        if record:
            return True
        else:
            DataFormatter.log_msg('Gagal menyimpan data', tag='supabase_error')
            return False