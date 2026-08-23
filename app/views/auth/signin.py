import flet as ft
import asyncio
import io
import random
import string
import base64
import urllib.parse
import jwt
import os
from pathlib import Path
from captcha.image import ImageCaptcha
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility import state, connection, config


def signin_view(page: ft.Page):

    storage = DataFormatter()
    current_captcha_text = ""

    def get_assets_dir():
        default_assets_dir = Path(__file__).parent / "assets"
        return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir)))

    font_path = get_assets_dir() / "fonts" / "Consolas.ttf"
    if font_path.exists():
        captcha_generator = ImageCaptcha(width=300, height=80, fonts=[str(font_path)])
    else:
        captcha_generator = ImageCaptcha(width=300, height=80)

    def generate_random_text(length=5):
        characters = string.ascii_uppercase + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def refresh_captcha_ui(e=None):
        nonlocal current_captcha_text
        current_captcha_text = generate_random_text()
        image_data = captcha_generator.generate(current_captcha_text, bg_color=(30, 30, 40), fg_color=(240, 240, 240))
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
        tooltip="Cek Koneksi..."
    )

    async def on_network_change(is_online: bool, connection_types):
        status_dot.bgcolor = ft.Colors.GREEN_400 if is_online else ft.Colors.RED_400
        status_dot.tooltip = "Online" if is_online else "Offline"
        try:
            status_dot.update()
        except Exception:
            pass
        if not is_online:
            DataFormatter.show_snackbar(page, "Koneksi internet bermasalah", "YELLOW_900")

    connection.Connectivity(page, on_change=on_network_change)

    def progress_signin_button():
        signin_button.disabled = True
        signin_button.icon = None
        signin_button.content = ft.ProgressRing(width=20, height=20, color=ft.Colors.YELLOW_400)
        page.update()

    def reset_signin_button():
        signin_button.disabled = False
        signin_button.icon = ft.Icons.FINGERPRINT
        signin_button.content = ft.Text("Masuk", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        page.update()

    def close_dialog(e):
        page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text(
            "Ooopsss..!!!",
            weight=ft.FontWeight.BOLD,
            size=14,
            color=ft.Colors.YELLOW_600,
            text_align=ft.TextAlign.CENTER
        ),
        content=ft.Text(
            "Silahkan hubungi admin...!!!",
            size=13,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER
        ),
        actions=[ft.TextButton("OK", on_click=close_dialog)],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def show_admin_contact(e):
        page.show_dialog(dialog)

    def signin_clicked(e):
        if not email_input.value.strip() or not password_input.value.strip():
            DataFormatter.show_snackbar(page, "Insert Email and Password..!!!", "YELLOW_900")
            return None
        if captcha_input.value.strip().upper() != current_captcha_text:
            DataFormatter.show_snackbar(page, "Kode Keamanan (CAPTCHA) tidak sesuai...!!!", "YELLOW_900")
            refresh_captcha_ui()
            return None
        progress_signin_button()
        page.run_task(validasi_user)

    async def next_focus(e, next_field):
        await asyncio.sleep(0.1)
        await next_field.focus()

    async def signup_account(e):
        try:
            if getattr(state, "register_status", None) == "close":
                show_admin_contact(e)
                return None
            page.navigate("/signup")
        except Exception as err:
            show_admin_contact(e)

    async def validasi_user():
        try:
            user_account = await Api.signin(email_input.value, password_input.value)
            if user_account and user_account.get("token"):
                token = user_account.get("token")
                user_payload = DataFormatter.decodetoken(token)
                username = user_payload.get("nama")
                await storage.set("current_user", user_payload)
                await storage.set("token", token)
                if not page.session.store.contains_key("current_user"):
                    page.session.store.set("current_user", user_payload)
                email_input.value = ""
                password_input.value = ""
                page.navigate("/home")
                DataFormatter.show_snackbar(page, f"Selamat Datang {username}", "GREEN_900")
                page.run_task(Api.useractivity, username, "Signin")
                return None
            else:
                DataFormatter.show_snackbar(page, "Username atau Password tidak sesuai...!!!", "YELLOW_900")
                refresh_captcha_ui()
                return None
        except Exception as err:
            DataFormatter.log_msg(f"{err}", tag="signin_error")
            DataFormatter.show_snackbar(
                page, "Koneksi internet bermasalah...!!!", "YELLOW_900"
            )
            return None
        finally:
            reset_signin_button()

    email_input = ft.TextField(
        width=310,
        label="email",
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.MARK_EMAIL_UNREAD,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        keyboard_type=ft.KeyboardType.EMAIL,
        autofill_hints=[ft.AutofillHint.EMAIL],
        on_submit=lambda e: page.run_task(next_focus, e, password_input)
    )

    password_input = ft.TextField(
        width=310,
        label="password",
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        password=True,
        can_reveal_password=True,
        autofill_hints=[ft.AutofillHint.PASSWORD],
        on_submit=lambda e: page.run_task(next_focus, e, captcha_input)
    )

    captcha_image = ft.Image(
        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
        width=150,
        height=40,
        fit=ft.BoxFit.CONTAIN
    )

    captcha_refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_color=ft.Colors.BLUE_400,
        on_click=refresh_captcha_ui,
        tooltip="Ganti Kode Baru"
    )

    captcha_input = ft.TextField(
        width=120,
        label="CAPTCHA",
        border=ft.InputBorder.UNDERLINE,
        border_color=ft.Colors.WHITE_30,
        focused_border_color=ft.Colors.BLUE_400,
        cursor_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        on_submit=signin_clicked,
        on_change=on_input_change
    )

    refresh_captcha_ui()

    signin_button = ft.Button(
        content=ft.Text("Masuk", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        width=310,
        height=50,
        bgcolor=ft.Colors.BLUE_600,
        icon=ft.Icons.FINGERPRINT,
        on_click=signin_clicked
    )

    app_icon = ft.Container(
        content=ft.Image(src="/images/icon.gif", width=200, height=200, fit=ft.BoxFit.CONTAIN, color=ft.Colors.WHITE),
        margin=ft.Margin(bottom=-35)
    )

    app_name = ft.Container(
        content=ft.Text(value=config.APP_NAME, size=25, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.CENTER
    )

    footer_text = ft.Container(
        content=ft.Text(
            "Copyright © 2026 RumahDjigo",
            size=12,
            color=ft.Colors.WHITE_70,
            weight=ft.FontWeight.W_300
        ),
        bottom=0,
        left=0,
        right=0,
        alignment=ft.Alignment.CENTER
    )

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
            web_only_window_name="_blank"
        )

    whatsapp_icon = ft.FloatingActionButton(
        content=ft.Image(src="/images/whatsapp.svg", width=30, height=30, fit=ft.BoxFit.COVER),
        width=45,
        height=45,
        bgcolor="#25D366",
        shape=ft.CircleBorder(),
        on_click=lambda e: page.run_task(call_admin, e),
        tooltip="Hubungi Admin"
    )

    signin_default_content = ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Column(
                            [app_icon, app_name, ft.Text(f"Versi {config.APP_VERSION}", size=17)],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                            margin=ft.Margin(bottom=10)
                        ),
                        ft.AutofillGroup(
                            content=ft.Column(
                                controls=[email_input, password_input],
                                spacing=0,
                                margin=ft.Margin(bottom=5)
                            )
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=captcha_image,
                                    alignment=ft.Alignment.CENTER
                                ),
                                captcha_refresh_btn,
                                ft.Container(content=captcha_input)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            width=310,
                            spacing=0
                        ),
                        ft.Row(
                            [
                                ft.Button(
                                    content=ft.Text("Lupa Password?", color=ft.Colors.BLUE_300),
                                    on_click=show_admin_contact
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            margin=ft.Margin(bottom=10, top=10),
                            width=310
                        ),
                        signin_button,
                        ft.Row(
                            [
                                ft.Text("Belum punya akun?", color=ft.Colors.WHITE),
                                ft.Button(
                                    content=ft.Text("Daftar Sekarang", color=ft.Colors.BLUE_300),
                                    on_click=signup_account
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            margin=ft.Margin(top=10),
                            width=310
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                    expand=True
                ),
                margin=ft.Margin(bottom=50)
            )
        ],
        expand=True
    )

    body_content = ft.Container(content=signin_default_content, expand=True)

    main_content = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [status_dot],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.Padding(left=10, top=10, right=10, bottom=0)
                        )
                    ],
                    spacing=0
                )
            ),
            body_content
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
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
                color=ft.Colors.GREY_800
            ),
            footer_text,
            main_container,
            ft.Container(content=whatsapp_icon, bottom=10, right=10)
        ]
    )

    return ft.View(
        route="/",
        padding=0,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(content=main_layout, alignment=ft.Alignment.CENTER, expand=True)
            )
        ]
    )