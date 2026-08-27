import flet as ft
import flet_geolocator as ftg
import asyncio
import httpx
from app.helpers.dataformatter import DataFormatter

async def get_current_location(page: ft.Page, geo: ftg.Geolocator):
    storage = DataFormatter()
    lokasi = {"ip_address": None, "latlong": None}
    try:
        limits = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=limits) as client:
            ip_response = await client.get("https://api.ipify.org")
            if ip_response.status_code == 200:
                lokasi["ip_address"] = ip_response.text.strip()
    except Exception as ip_err:
        DataFormatter.log_msg(f"{ip_err}", tag="ipaddress_error")
    try:
        status = await geo.get_permission_status()
        if (status.value in ["denied", "unknown"] or status == ftg.GeolocatorPermissionStatus.DENIED):
            result = await geo.request_permission()
            if (result.value in ["denied", "deniedForever"] or result == ftg.GeolocatorPermissionStatus.DENIED):
                DataFormatter.show_snackbar(page, "Ijin ditolak, silahkan aktifkan di pengaturan Android", "YELLOW_900")
                await geo.open_app_settings()
                page.update()
                return None
        p = None
        for attempt in range(3):
            p = await geo.get_current_position()
            if p:
                break
            await asyncio.sleep(1.0)
        if p:
            lokasi["latlong"] = f"{p.latitude},{p.longitude}"
            await storage.set("current_location", lokasi)
            return lokasi
        else:
            DataFormatter.show_snackbar(page, "Aktifkan Lokasi Perangkat Anda!", "YELLOW_900")
            await geo.open_location_settings()
            page.update()
            return None
    except Exception as err:
        DataFormatter.show_snackbar(page, f"{err}", "YELLOW_900")
        DataFormatter.log_msg(f"{err}", tag="aplikasi_error")
        return None