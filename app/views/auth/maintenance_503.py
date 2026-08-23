import flet as ft


def maintenance_503_view(page: ft.Page):
    main_content = ft.Column(
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=ft.Image(
                    src="/images/alien.svg",
                    fit=ft.BoxFit.CONTAIN,
                    color=ft.Colors.WHITE_70,
                ),
                width=280,
                height=280,
                alignment=ft.Alignment.CENTER
            ),
            ft.Container(
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Text(
                            value="503",
                            size=65,
                            weight=ft.FontWeight.BOLD,
                            color="#2ccf6d"
                        ),
                        ft.Text(
                            value="Oooups! Service Unavailable...",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            value="The system is currently undergoing routine maintenance. Please wait a moment, and we apologize for any inconvenience caused!",
                            size=16,
                            color=ft.Colors.WHITE_70,
                            text_align=ft.TextAlign.CENTER
                        )
                    ]
                )
            )
        ]
    )

    main_container = ft.Container(
        content=main_content,
        width=390,
        height=844,
        padding=15,
        alignment=ft.Alignment.CENTER
    )

    footer = ft.Container(
        content=ft.Text(
            value=f"Copyright © 2026 RumahDjigo",
            size=12,
            color=ft.Colors.WHITE_70,
            weight=ft.FontWeight.W_300
        ),
        bottom=5,
        left=0,
        right=0,
        alignment=ft.Alignment.CENTER
    )

    main_layout = ft.Stack(
        controls=[
            ft.Image(
                src="/images/background.png",
                fit=ft.BoxFit.COVER,
                width=390,
                height=844,
                gapless_playback=True,
                color=ft.Colors.GREY_800
            ),
            main_container,
            footer
        ],
        expand=True
    )

    return ft.View(
        route="/404",
        padding=0,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(content=main_layout, alignment=ft.Alignment.CENTER, expand=True)
            )
        ]
    )