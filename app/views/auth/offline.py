import flet as ft
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility import connection


def offline_view(page: ft.Page, on_retry_click):
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

        if not is_online:
            DataFormatter.show_snackbar(
                page, "Koneksi internet bermasalah", "YELLOW_900"
            )

    connection.Connectivity(page, on_change=on_network_change)

    offline_default_content = ft.Column(
        controls=[
            ft.Icon(ft.Icons.WIFI_OFF_ROUNDED, color=ft.Colors.RED_400, size=50),
            ft.Text(
                "Koneksi Bermasalah",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Text(
                "Koneksi internet bermasalah atau server tidak merespons.\nSilakan ulangi beberapa saat lagi...!!!",
                size=13,
                color=ft.Colors.GREY_400,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=10),
            ft.FilledButton(
                "Coba Lagi",
                on_click=on_retry_click,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
    )

    body_content = ft.Container(content=offline_default_content, expand=True)

    main_content = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [status_dot],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.Padding(left=10, top=10, right=10, bottom=10),
                        )
                    ],
                    spacing=0,
                )
            ),
            body_content,
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
        route="/loading",
        padding=0,
        fullscreen_dialog=True,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    content=main_layout, alignment=ft.Alignment.CENTER, expand=True
                ),
            )
        ],
    )
