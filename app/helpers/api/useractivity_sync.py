import httpx
import sqlite3
import asyncio
from typing import Dict, Any, List
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config

class UserActivitySync:

    DB_NAME = "project.db"

    @classmethod
    async def useractivity_sync(cls) -> dict:
        def _fetch_all_pending() -> List[Dict[str, Any]]:
            try:
                with sqlite3.connect(cls.DB_NAME) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, datetime_created, app_name, username, last_activity, ip_address, lat_long FROM user_activities")
                    return [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                DataFormatter.log_msg(f"{err}", tag="sqlitesync_error")
                return []

        pending_records = await asyncio.to_thread(_fetch_all_pending)
        if not pending_records:
            return {"status": "success", "synced": 0, "failed": 0}
        timeout = httpx.Timeout(20.0, connect=10.0)
        transport = httpx.AsyncHTTPTransport(retries=3)
        query_params = {"page": "useractivity"}
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
            async def _send_record(record: dict):
                record_id = record.pop("id")
                try:
                    response = await client.post(url=config.API_URL, headers=config.HEADERS, params=query_params, json=record)
                    if response.is_success:
                        return True, record_id
                    else:
                        DataFormatter.log_msg(f"failed sync ID {record_id}: {response.status_code}", tag="syncpending_error")
                        return False, record_id
                except Exception as err:
                    DataFormatter.log_msg(f"Exception sync ID {record_id}: {err}", tag="syncpending_error")
                    return False, record_id

            results = await asyncio.gather(*[_send_record(rec) for rec in pending_records])
        synced_ids = [rid for success, rid in results if success]
        failed_count = len(results) - len(synced_ids)
        if synced_ids:
            def _delete_batch(ids: list[int]):
                try:
                    with sqlite3.connect(cls.DB_NAME) as conn:
                        placeholders = ",".join("?" for _ in ids)
                        conn.execute(f"DELETE FROM user_activities WHERE id IN ({placeholders})", ids,)
                        conn.commit()
                except sqlite3.Error as err:
                    DataFormatter.log_msg(f"{err}", tag="syncdelete_error")
            await asyncio.to_thread(_delete_batch, synced_ids)
        return {"status": "completed", "synced": len(synced_ids), "failed": failed_count}