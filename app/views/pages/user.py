import flet as ft
import io
import qrcode
import base64
import urllib.parse
from app.helpers.utility import config
from app.helpers.api import Api


def user_view(page: ft.Page):
    profile = page.session.store.get("current_user") or {}
    user_name = profile.get("nama", "-")
    user_image = profile.get("image", "-")
    user_email = profile.get("email", "-")
    no_telp = profile.get("no_telp", "-")
    url_whatsapp = (f"https://wa.me/{no_telp}?text={urllib.parse.quote(f'Hallo {user_name}...')}")
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(url_whatsapp if url_whatsapp else "-")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    qr_base64 = base64.b64encode(img_bytes).decode("utf-8")
    qr_data_url = f"data:image/png;base64,{qr_base64}"
    user_qr_code = ft.Image(src=qr_data_url, width=150, height=150, fit=ft.BoxFit.CONTAIN)

    username = ft.Container(
        content=ft.Text(value=user_name, size=20, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.CENTER,
        margin=ft.Margin(top=20)
    )

    user_icon = ft.Container(
        content=ft.CircleAvatar(foreground_image_src=f"{config.API_CDN}/images/{user_image}", radius=70),
        alignment=ft.Alignment.CENTER
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
        alignment=ft.Alignment.CENTER
    )

    home_default_content = ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    [user_icon, username, ft.Text(value=user_email, size=15), ft.Container(height=10), user_qr_code],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                alignment=ft.Alignment.CENTER,
                expand=True
            ),
            footer_text
        ],
        expand=True
    )

    main_container = ft.Container(content=home_default_content, expand=True)

    main_layout = ft.Stack(
        controls=[
            ft.Column(
                controls=[main_container],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                expand=True
            )
        ],
        expand=True
    )

    page.run_task(Api.useractivity, user_name, f"View User Account Page")

    return ft.Container(
        content=main_layout,
        padding=ft.Padding(left=10, top=10, right=10, bottom=0),
        expand=True
    )