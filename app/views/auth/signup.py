import flet as ft
import asyncio
import io
import re
import random
import string
import base64
import urllib.parse
import os
from pathlib import Path
from captcha.image import ImageCaptcha
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility import connection, config


def signup_view(page: ft.Page):

    def get_assets_dir() -> Path:
        default_assets_dir = Path(__file__).parent / "assets"
        return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir)))

    font_path = get_assets_dir() / "fonts" / "Rubrik.otf"
    if font_path.exists():
        captcha_generator = ImageCaptcha(width=300, height=80, fonts=[str(font_path)])
    else:
        captcha_generator = ImageCaptcha(width=300, height=80)

    current_captcha_text = ""

    def generate_random_text(length=5):
        characters = string.ascii_uppercase + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def refresh_captcha_ui(e=None):
        nonlocal current_captcha_text
        current_captcha_text = generate_random_text()
        image_data = captcha_generator.generate(
            current_captcha_text, bg_color=(30, 30, 40), fg_color=(240, 240, 240)
        )
        image_bytes = io.BytesIO(image_data.read())
        raw_bytes = image_bytes.getvalue()
        base64_string = base64.b64encode(raw_bytes).decode("utf-8")
        captcha_image.src = f"data:image/png;base64,{base64_string}"
        captcha_input.value = ""
        page.update()

    def on_input_change(e):
        captcha_input.value = captcha_input.value.upper()
        page.update()

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

    def progress_signup_button():
        signup_button.disabled = True
        signup_button.icon = None
        signup_button.content = ft.ProgressRing(
            width=20, height=20, color=ft.Colors.YELLOW_400
        )
        page.update()

    def reset_signup_button():
        signup_button.disabled = False
        signup_button.icon = ft.Icons.FINGERPRINT
        signup_button.content = ft.Text(
            "Masuk", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
        )
        page.update()

    def signup_clicked(e):
        error_message = None
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if (
            not nama_input.value.strip()
            or not email_input.value.strip()
            or not phone_input.value.strip()
            or not password_input.value.strip()
        ):
            error_message = "Silahkan lengkapi data anda...!!!"

        elif len(nama_input.value) < 3:
            error_message = "Nama minimal 3 karakter...!!!"
        elif not re.match(email_pattern, email_input.value):
            error_message = "Email tidak valid...!!!"
        elif not phone_input.value.isdigit():
            error_message = "No telpon tidak valid...!!!"
        elif len(phone_input.value) < 10:
            error_message = "No telpon minimal 10 digit...!!!"
        elif len(password_input.value) < 3:
            error_message = "Password minimal 3 karakter...!!!"

        if error_message:
            DataFormatter.show_snackbar(page, error_message, "YELLOW_900")
            return

        if captcha_input.value.strip().upper() != current_captcha_text:
            DataFormatter.show_snackbar(
                page, "Kode Keamanan (CAPTCHA) tidak sesuai...!!!", "YELLOW_900"
            )
            refresh_captcha_ui()
            return

        page.run_task(send_data_signup)

    async def next_focus(e, next_field):
        await asyncio.sleep(0.1)
        await next_field.focus()
        page.update()

    nama_input = ft.TextField(
        width=310,
        label="Nama Lengkap",
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.ACCOUNT_CIRCLE,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        on_submit=lambda e: page.run_task(next_focus, e, email_input),
    )

    email_input = ft.TextField(
        width=310,
        label="Email",
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.MARK_EMAIL_UNREAD,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        keyboard_type=ft.KeyboardType.EMAIL,
        on_submit=lambda e: page.run_task(next_focus, e, phone_input),
    )

    phone_input = ft.TextField(
        width=310,
        label="Nomor Telpon",
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.PHONE_ANDROID_ROUNDED,
        prefix=ft.Text("+62 ", color=ft.Colors.WHITE),
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        keyboard_type=ft.KeyboardType.PHONE,
        on_submit=lambda e: page.run_task(next_focus, e, password_input),
    )

    password_input = ft.TextField(
        width=310,
        label="Password",
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        password=True,
        can_reveal_password=True,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        keyboard_type=ft.KeyboardType.PHONE,
        on_submit=lambda e: page.run_task(next_focus, e, captcha_input),
    )

    captcha_image = ft.Image(
        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
        width=150,
        height=40,
        fit=ft.BoxFit.CONTAIN,
    )

    captcha_refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_color=ft.Colors.BLUE_400,
        on_click=refresh_captcha_ui,
        tooltip="Ganti Kode Baru",
    )

    captcha_input = ft.TextField(
        width=120,
        label="CAPTCHA",
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        on_submit=signup_clicked,
        on_change=on_input_change,
    )

    refresh_captcha_ui()

    signup_button = ft.Button(
        content=ft.Text("Daftar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        width=310,
        height=50,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        icon=ft.Icons.SEND,
        on_click=signup_clicked,
    )

    app_icon = ft.Container(
        content=ft.Image(
            src="/images/icon.gif", width=200, height=200, fit=ft.BoxFit.CONTAIN, color=ft.Colors.WHITE
        ),
        margin=ft.Margin(bottom=-20)
    )

    app_name = ft.Container(
        content=ft.Text(value=config.APP_NAME, size=25, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.CENTER,
    )

    footer_text = ft.Container(
        content=ft.Text(
            "Copyright © 2026 RumahDjigo",
            size=12,
            color=ft.Colors.WHITE_70,
            weight=ft.FontWeight.W_300,
        ),
        bottom=0,
        left=0,
        right=0,
        alignment=ft.Alignment.CENTER,
    )

    async def send_data_signup():
        progress_signup_button()

        try:
            await Api.useractivity(
                nama_input.value.strip().title(), "Registrasi Akun"
            )
        except Exception as err:
            DataFormatter.log_msg(
                "Koneksi internet bermasalah", "postuseractivity_error"
            )
            return

        phone_value = phone_input.value.strip()
        if phone_value.startswith("0"):
            phone_value = phone_value[1:]

        result = await Api.signup(
            nama=nama_input.value.strip(),
            email=email_input.value.strip(),
            no_telp=f"'+62{phone_value}",
            password=password_input.value,
        )

        reset_signup_button()

        if result.get("status") == "success":
            await asyncio.sleep(0.1)
            page.navigate("/signin")
            DataFormatter.show_snackbar(page, "Registrasi berhasil...!!!", "GREEN_900")
            return

        elif result.get("status") == "error || 404":
            DataFormatter.show_snackbar(
                page, f"Registrasi gagal:\nPendaftaran ditutup...!!!", "YELLOW_900"
            )
            return

        else:
            DataFormatter.show_snackbar(
                page,
                f"{result.get('message', 'Gagal terhubung ke server.')}",
                "YELLOW_900",
            )
            return

    async def login_akun(e):
        page.navigate("/signin")

    nomor_wa = None
    if page.session.store.contains_key("info_app"):
        for item in page.session.store.get("info_app"):
            if item.get("info") == "project_admin":
                nomor_wa = item.get("message")
                break

    async def call_admin(e):
        await ft.UrlLauncher().launch_url(
            f"https://wa.me/{nomor_wa}?text={urllib.parse.quote('Hallo admin...???')}",
            mode=ft.LaunchMode.EXTERNAL_APPLICATION,
            web_only_window_name="_blank",
        )

    whatsapp_icon = ft.FloatingActionButton(
        content=ft.Image(
            src="/images/whatsapp.svg", width=30, height=30, fit=ft.BoxFit.COVER
        ),
        width=45,
        height=45,
        bgcolor="#25D366",
        shape=ft.CircleBorder(),
        on_click=lambda e: page.run_task(call_admin, e),
        tooltip="Hubungi Admin",
    )

    signup_default_content = ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Column(
                            [
                                app_icon,
                                app_name,
                                ft.Text(f"Versi {config.APP_VERSION}", size=17),
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                        ft.Column(
                            [
                                nama_input,
                                email_input,
                                phone_input,
                                password_input,
                            ],
                            spacing=0,
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=captcha_image,
                                    alignment=ft.Alignment.CENTER_LEFT,
                                ),
                                captcha_refresh_btn,
                                ft.Container(
                                    content=captcha_input,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            width=310,
                            spacing=0,
                        ),
                        signup_button,
                        ft.Row(
                            [
                                ft.Text("Sudah punya akun?", color=ft.Colors.WHITE),
                                ft.Button(
                                    content=ft.Text("Login", color=ft.Colors.BLUE_300),
                                    on_click=login_akun,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            width=310,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                margin=ft.Margin(bottom=50)
            ),
        ],
        expand=True,
    )

    body_content = ft.Container(content=signup_default_content, expand=True)

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
                            padding=ft.Padding(left=10, top=10, right=10, bottom=0),
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
            footer_text,
            main_container,
            ft.Container(content=whatsapp_icon, bottom=10, right=10),
        ]
    )

    return ft.View(
        route="/signup",
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
