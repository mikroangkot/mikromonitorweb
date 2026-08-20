import flet as ft
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility import connection, config
from app.views.pages import user


def home_view(page: ft.Page):

    storage = DataFormatter()
    profile = page.session.store.get("current_user") or {}
    user_name = profile.get("nama", "-")
    user_image = profile.get("image", "-")

    status_dot = ft.Container(
        width=13,
        height=13,
        border_radius=6.5,
        bgcolor=ft.Colors.GREY_500,
        tooltip="Cek Koneksi...",
    )

    async def on_network_change(is_online: bool, connection_types):
        status_dot.bgcolor = ft.Colors.GREEN_400 if is_online else ft.Colors.RED_400
        status_dot.tooltip = "Online" if is_online else "Offline"
        try:
            status_dot.update()
        except Exception:
            pass

    connection.Connectivity(page, on_change=on_network_change)

    async def proses_logout(e):
        page.pop_dialog()
        page.views.clear()
        page.navigate("/loading")

        try:
            await Api.useractivity(user_name, "Signout")
        except Exception as err:
            DataFormatter.log_msg("koneksi bermasalah", tag="signout_error")

        await storage.remove("token")
        page.session.store.remove("current_user")
        page.navigate("/signin")

    def open_profile(e):
        body_content.content = user.user_view(page)
        body_content.update()

    def close_dialog(e):
        page.pop_dialog()

    confirm_dialog = ft.AlertDialog(
        title=ft.Text(
            "Konfirmasi Signout",
            weight=ft.FontWeight.BOLD,
            size=14,
            color=ft.Colors.YELLOW_600,
        ),
        content=ft.Text(
            "Yakin Akan Signout...?",
            size=13,
            color=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Batal", on_click=close_dialog),
            ft.TextButton("Ya", on_click=proses_logout),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_confirm_logout(e):
        page.show_dialog(confirm_dialog)

    user_profile = ft.PopupMenuButton(
        padding=0,
        content=ft.Row(
            [
                ft.Text(
                    value=user_name,
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(
                    content=ft.Image(
                        src=f"{config.API_CDN}/images/{user_image}",
                        fit=ft.BoxFit.COVER,
                    ),
                    width=25,
                    height=25,
                    border_radius=18,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
            ],
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        items=[
            ft.PopupMenuItem(
                icon=ft.Icons.PERSON,
                content=ft.Text(value="My Account", size=12),
                on_click=open_profile,
                height=15,
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                icon=ft.Icons.LOGOUT,
                content=ft.Text(value="Signout", size=12),
                on_click=open_confirm_logout,
                height=15,
            ),
        ],
    )

    app_icon = ft.Container(
        content=ft.Image(
            src="/images/icon.gif", width=200, height=200, fit=ft.BoxFit.CONTAIN, color=ft.Colors.WHITE
        ),
        alignment=ft.Alignment.CENTER,
        margin=ft.Margin(bottom=-35)
    )

    app_name = ft.Container(
        content=ft.Text(value=config.APP_NAME, size=25, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.CENTER,
        margin=ft.Margin(top=10),
    )

    footer_text = ft.Container(
        content=ft.Text(
            f"Copyright © 2026 RumahDjigo",
            size=12,
            color=ft.Colors.WHITE_70,
            weight=ft.FontWeight.W_300,
        ),
        bottom=0,
        left=0,
        right=0,
        margin=ft.Margin(bottom=-5),
        alignment=ft.Alignment.CENTER,
    )

    home_default_content = ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    [
                        app_icon,
                        app_name,
                        ft.Text(f"Versi {config.APP_VERSION}", size=17),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
            footer_text,
        ],
        expand=True,
    )

    body_content = ft.Container(content=home_default_content, expand=True)

    def on_nav_change(e):

        selected_label = e.control.destinations[e.control.selected_index].label
        if selected_label == "Home":
            body_content.content = home_default_content
        elif selected_label == "Unit":
            # body_content.content = unit.unit_view(page)
            body_content.content = home_default_content
        elif selected_label == "KM Baku":
            body_content.content = home_default_content
        elif selected_label == "History":
            body_content.content = home_default_content
        elif selected_label == "Headway":
            body_content.content = home_default_content
        else:
            body_content.content = ft.Container(
                content=ft.Text(f"Halaman {selected_label}", size=20),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )

        body_content.update()

    nav_destinations = [
        ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
        ft.NavigationBarDestination(icon=ft.Icons.DIRECTIONS_BUS, label="Unit"),
        ft.NavigationBarDestination(icon=ft.Icons.SPEED, label="KM Baku"),
        ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="History"),
        ft.NavigationBarDestination(icon=ft.Icons.AV_TIMER, label="Headway")
    ]

    my_navbar = ft.Container(
        content=ft.NavigationBar(
            destinations=nav_destinations,
            selected_index=0,
            on_change=on_nav_change,
            indicator_color=ft.Colors.BLUE_900,
        ),
        width=390,
    )

    main_content = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [status_dot, user_profile],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.Padding(left=10, top=10, right=10, bottom=10),
                        ),
                        ft.Divider(height=1, thickness=0.5, color=ft.Colors.WHITE_70),
                    ],
                    spacing=0,
                )
            ),
            body_content,
            my_navbar,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    main_container = ft.Container(content=main_content, width=390, height=844)

    main_layout = ft.Stack(
        controls=[
            ft.Image(
                src="/images/background.png",
                fit=ft.BoxFit.COVER,
                width=390,
                height=844,
                gapless_playback=True,
                color=ft.Colors.GREY_800,
            ),
            main_container,
        ]
    )

    return ft.View(
        route="/home",
        padding=0,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    content=main_layout, alignment=ft.Alignment.CENTER, expand=True
                ),
            )
        ],
    )
