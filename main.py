import flet as ft
import flet_geolocator as ftg
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.views.pages import Pages
from app.helpers.utility import (state, location, init_db, router, info_server, config)
from app.views.auth import (signin, signup, notfound_404, maintenance_503, loading, offline)

async def main(page: ft.Page):
    page.title = config.APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {"Rubrik": "/fonts/Rubrik.otf"}
    page.theme = ft.Theme(font_family="Rubrik")
    page.safe_area = True
    page.adaptive = True
    page.resize_to_avoid_bottom_inset = True
    page.padding = 0
    page.window_width = 390
    page.window_height = 844

    wakelock = ft.Wakelock()
    storage = DataFormatter()
    profile = page.session.store.get("current_user") or {}
    user_name = profile.get("nama", "-")
    geo = ftg.Geolocator(configuration=ftg.GeolocatorConfiguration(accuracy=ftg.GeolocatorPositionAccuracy.HIGH))
    app_router = router.Router(page)

    async def wakelock_enable():
        try:
            await wakelock.enable()
        except Exception as err:
            DataFormatter.log_msg(err)
    
    def close_dialog_exit(e):
        page.pop_dialog()

    async def confirm_exit(e):
        page.pop_dialog()
        page.navigate("/loading")
        try:
            await Api.post_user_activity(user_name, "Signout App")
        except Exception as err:
            DataFormatter.log_msg("koneksi internet bermasalah", tag="postuseractivity_error")
        page.session.store.remove("current_user")
        await storage.remove("current_user")
        await storage.remove("token")
        await storage.remove("dataunit")
        await storage.remove("datakmbaku")
        page.navigate("/signin")

    dialog_exit = ft.AlertDialog(
        title=ft.Text("Confirm", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.YELLOW_600),
        content=ft.Text("Apakah yakin ingin keluar dari aplikasi?", size=13, color=ft.Colors.WHITE),
        actions=[ft.TextButton("Batal", on_click=close_dialog_exit), ft.TextButton("Ya", on_click=confirm_exit)],
        actions_alignment=ft.MainAxisAlignment.END
    )

    async def confirm_exit_log(e):
        page.show_dialog(dialog_exit)

    def build_home_view(p: ft.Page):
        h_view = Pages.home_view(p)
        h_view.can_pop = False
        h_view.on_confirm_pop = confirm_exit_log
        return h_view

    def build_offline_view(p: ft.Page):
        retry_callback = getattr(state, "on_retry_click", None)
        return offline.offline_view(p, on_retry_click=retry_callback)

    app_router.add_route("/", loading.loading_view)
    app_router.add_route("/loading", loading.loading_view)
    app_router.add_route("/signin", signin.signin_view, guest_only=True)
    app_router.add_route("/signup", signup.signup_view, guest_only=True)
    app_router.add_route("/home", build_home_view, protected=True)
    app_router.add_route("/503", maintenance_503.maintenance_503_view)
    app_router.add_route("/404", notfound_404.notfound_404_view)
    app_router.add_route("/offline", build_offline_view)

    async def handle_lifecycle_change(e: ft.AppLifecycleStateChangeEvent):
        if e.state == "resumed":
            await location.get_current_location(page, geo)
            user_saved = await storage.get("current_user")
            if user_saved and not page.session.store.contains_key("current_user"):
                page.session.store.set("current_user", user_saved)

    async def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.route = top_view.route
            page.update()

    page.on_app_lifecycle_state_change = handle_lifecycle_change
    page.on_view_pop = view_pop

    async def init_cek():
        page.navigate("/loading")
        await info_server.info_server(page)
        await location.get_current_location(page, geo)

    await init_cek()
    await wakelock_enable()

ft.run(main, assets_dir="assets")
