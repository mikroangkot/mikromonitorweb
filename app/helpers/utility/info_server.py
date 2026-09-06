import flet as ft
import asyncio
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility import state, config
from app.views.auth import offline, loading

async def info_server(page: ft.Page):
    storage = DataFormatter()
    while True:
        try:
            data_list = await Api.info_app()
            if not data_list:
                raise ConnectionError("Gagal terhubung ke server...")
            for list_info in data_list:
                info = list_info.get("info")
                message = list_info.get("message")
                if not info or not message:
                    continue
                if info == "project_register":
                    state.register_status = message
                    page.register_status = message
                if info == "project_status":
                    state.server_status = message
                    page.server_status = message
                    if message == "close":
                        await page.push_route("/503")
                        return None
                if info == "project" and message:

                    async def close_banner(e):
                        page.pop_dialog()

                    banner = ft.Banner(
                        leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.PRIMARY),
                        content=ft.Text(message, size=11),
                        actions=[ft.TextButton(ft.Text("Dismiss", size=11), on_click=close_banner)],
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                        open=True
                    )
                    page.show_dialog(banner)
            if not page.session.store.contains_key("info_app"):
                page.session.store.set("info_app", data_list)
            break
        except Exception:
            button_click = asyncio.Event()

            async def coba_lagi(e):
                button_click.set()
                page.navigate("/loading")

            state.on_retry_click = coba_lagi
            page.navigate("/offline")
            await button_click.wait()
    user_saved = await storage.get("current_user")
    if user_saved:
        page.session.store.set("current_user", user_saved)
    if getattr(page, "server_status", "open") != "close":
        initial_route = ("/home" if page.session.store.contains_key("current_user") else "/signin")
        page.navigate(initial_route)