import httpx
import sqlite3
import asyncio
from typing import Optional
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config

class UserActivity:

    DB_NAME = "project.db"

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
        def _insert_local() -> Optional[int]:
            try:
                with sqlite3.connect(UserActivity.DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
						INSERT INTO user_activities (app_name, username, last_activity, ip_address, lat_long)
						VALUES (:app_name, :username, :last_activity, :ip_address, :lat_long)
						""",
                        payload,
                    )
                    conn.commit()
                    return cursor.lastrowid
            except sqlite3.Error as err:
                DataFormatter.log_msg(f"{err}", tag="sqlite_error")
                return None
        record_id = await asyncio.to_thread(_insert_local)
        try:
            timeout = httpx.Timeout(20.0, connect=10.0)
            transport = httpx.AsyncHTTPTransport(retries=3)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
                response = await client.post(url=config.API_URL, headers=config.HEADERS, params=query_params, json=payload)
                if response.is_success:
                    if record_id:
                        def _delete_local(rid: int):
                            with sqlite3.connect(UserActivity.DB_NAME) as conn:
                                conn.execute("DELETE FROM user_activities WHERE id = ?", (rid,))
                                conn.commit()
                        await asyncio.to_thread(_delete_local, record_id)
                    return True
                else:
                    DataFormatter.log_msg(f"{response.status_code}", tag="postuseractivity_error")
        except Exception as err:
            DataFormatter.log_msg(f"{err}", tag="postuseractivity_error")
        return False