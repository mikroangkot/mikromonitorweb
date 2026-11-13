import flet as ft
import httpx
import io
import asyncio
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.datetime_indo import format_tanggal_hari, format_jam

def build_excel(report):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = ["No", "Hari/Tanggal", "Jam", "App Name", "Nama", "Email", "Last Activity", "IP Address", "Location", "User ID", "Last Signin", "Active At"]
	ws.append(headers)
	ws.freeze_panes = "A2"
	font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
	fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
	for col_num, header in enumerate(headers, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.font = font_header
		cell.fill = fill_header
	for index, item in enumerate(report):
		ws.append(
			[
				item.get("no"),
				format_tanggal_hari(item.get("created_at")),
				format_jam(item.get("created_at")),
				item.get("app_name"),
				item.get("username"),
				item.get("email"),
				item.get("last_activity").title(),
				item.get("ip_address"),
				item.get("lat_long"),
				item.get("uid"),
				item.get("last_signin"),
				item.get("email_confirmed_at")
			]
		)
	kolom_terakhir = openpyxl.utils.get_column_letter(len(headers))
	baris_terakhir = ws.max_row
	ws.auto_filter.ref = f"A1:{kolom_terakhir}{baris_terakhir}"
	align_center_data = Alignment(horizontal="center", vertical="center")
	for col in ws.columns:
		max_len = max(len(str(cell.value or "")) for cell in col)
		col_letter = openpyxl.utils.get_column_letter(col[0].column)
		ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
	excel_stream = io.BytesIO()
	wb.save(excel_stream)
	excel_stream.seek(0)
	return excel_stream.getvalue()

def usersreport_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"report": []}
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)
	share = ft.Share()
	storage = DataFormatter()

	async def share_excel(e):
		if not state_data["report"]:
			DataFormatter.show_snackbar(page, "Tidak ada data...!!!", "YELLOW_900")
			return None
		btn_share.disabled = True
		btn_share.icon = None
		btn_share.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		default_file_name = "Users Report Activity.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["report"])
			excel_file = ft.ShareFile.from_bytes(excel_bytes, name=default_file_name, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			await share.share_files([excel_file], text=default_file_name)
			page.run_task(Api.useractivity, username, f"Share {default_file_name}")
			btn_share.visible = False
		except Exception as err:
			DataFormatter.show_snackbar(page, f"Failed Share Data: {err}", "YELLOW_900")
		btn_share.disabled = False
		btn_share.icon = ft.Icons.SHARE
		btn_share.content = ft.Text("Share Data")
		page.update()

	api_result_container = ft.Column(
		controls=[daftar_konten],
		scroll=ft.ScrollMode.AUTO,
		horizontal_alignment=ft.CrossAxisAlignment.START,
		alignment=ft.MainAxisAlignment.START,
		expand=True
	)

	loading_spinner = ft.Container(
		content=ft.Column(
			controls=[ft.ProgressRing(width=45, height=45, color=ft.Colors.YELLOW_400), ft.Text("Sedang memuat data...", size=13, color=ft.Colors.WHITE)],
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			alignment=ft.MainAxisAlignment.CENTER,
			spacing=15
		),
		alignment=ft.Alignment(0, 0),
		visible=False,
		expand=True
	)

	btn_share = ft.Button(
		content=ft.Text("Share Data", size=13),
		width=333,
		style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
		icon=ft.Icons.SHARE,
		on_click=share_excel,
		visible=False
	)

	hasil_pencarian = ft.Text("0", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW_400)
	rekapan = ft.Container(
		content=ft.Row(
			controls=[
				ft.Container(
					expand=True,
					content=ft.Card(
						content=ft.Container(
							content=ft.Row(
								controls=[
									ft.Column(
										controls=[
											ft.Text("TOTAL DATA :", size=13, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
											hasil_pencarian
										],
										spacing=0,
										alignment=ft.MainAxisAlignment.CENTER,
										horizontal_alignment=ft.CrossAxisAlignment.START
									)
								],
								spacing=15,
								alignment=ft.MainAxisAlignment.START
							),
							padding=ft.Padding.symmetric(horizontal=12, vertical=6)
						),
						bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
						elevation=2
					)
				)
			],
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			spacing=5
		),
		margin=ft.Margin(top=6, bottom=0),
		visible=False
	)

	async def muat_data():
		daftar_konten.controls.clear()
		rekapan.visible = False
		btn_share.visible = False
		loading_spinner.visible = True
		page.update()
		try:
			raw_data = await Api.usersactivityreport() or []
			state_data["report"] = raw_data
			total_data = f"{len(raw_data):,}".replace(",", ".")
			if len(raw_data) == 0:
				DataFormatter.show_snackbar(page, "Data Tidak Ditemukan...", "YELLOW_900")
				return None
			for item in raw_data[:50]:
				item_box = ft.Column(
					controls=[
						ft.Text(f"No: {item.get('no')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Hari/Tanggal: {format_tanggal_hari(item.get('created_at'))}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Jam: {format_jam(item.get('created_at'))}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"App Name: {item.get('app_name')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Nama: {item.get('username')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Email: {item.get('email')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Last Activity: {item.get('last_activity').title()}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"IP Address: {item.get('ip_address')}", size=13, color=ft.Colors.WHITE),
						ft.Text(
							spans=[
								ft.TextSpan("Location: "),
								ft.TextSpan(text=item.get("lat_long"),
								url=item.get("lat_long"),
								style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,
								color=ft.Colors.BLUE_400))
							],
							size=13,
							color=ft.Colors.WHITE
						),
						ft.Text(f"User ID: {item.get('uid')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Last Signin: {item.get('last_signin')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Active At: {item.get('email_confirmed_at')}", size=13, color=ft.Colors.WHITE),
						ft.Divider(thickness=0.5, color=ft.Colors.GREY_600)
					],
					spacing=0.5
				)
				daftar_konten.controls.append(item_box)
			hasil_pencarian.value = total_data
			rekapan.visible = True
			btn_share.visible = True
			page.run_task(Api.useractivity, username, "View User Report History")
		except httpx.TimeoutException:
			DataFormatter.show_snackbar(page, "Request timout error", "YELLOW_900")
			return None
		except Exception as err:
			DataFormatter.show_snackbar(page, f"{err}", "YELLOW_900")
			return None
		finally:
			loading_spinner.visible = False
			page.update()

	page.run_task(muat_data)

	main_layout = ft.Stack(
		controls=[
			ft.Column(
				controls=[
					rekapan,
					ft.Container(content=api_result_container, expand=True),
					btn_share
				],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				expand=True
			),
			loading_spinner
		],
		expand = True
	)

	return ft.Container(
		content=main_layout,
		padding=ft.Padding(left=10, top=-10, right=10),
		expand = True
	)