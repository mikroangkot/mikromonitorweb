import flet as ft


def loading_view(page: ft.Page):
    main_content = ft.Column(
        controls=[
            ft.ProgressRing(width=45, height=45, color=ft.Colors.BLUE_400),
            ft.Text("Please wait...", size=13, color=ft.Colors.WHITE),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
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
