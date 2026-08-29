import flet as ft
import httpx
import io
import asyncio
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
from app.helpers.utility import config
from app.helpers.api import Api
from app.helpers.dataformatter import DataFormatter

def build_excel(data_kmbaku):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = ["Rute", "Rute Layanan", "Nama Trip", "KM Baku", "Keterangan"]
	ws.append(headers)
	ws.freeze_panes = "A2"
	font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
	fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
	for col_num, header in enumerate(headers, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.font = font_header
		cell.fill = fill_header
	for index, item in enumerate(data_kmbaku):
		ws.append(
			[
				item.get("rute"),
				item.get("rute_layanan"),
				item.get("trip_name"),
				item.get("km_baku"),
				item.get("keterangan")
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

def kmbaku_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"data_history": []}
	status_text = ft.Text(value="")
	rekapan = ft.Container(content=ft.Row(controls=[status_text]))
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)
	share = ft.Share()

	async def share_excel(e):
		if not state_data["data_kmbaku"]:
			DataFormatter.show_snackbar(page, "Tidak ada data...!!!", "YELLOW_900")
			return None
		btn_share.disabled = True
		btn_share.icon = None
		btn_share.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		default_file_name = f"Data KM Baku {search_input.value}.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["data_kmbaku"])
			excel_file = ft.ShareFile.from_bytes(excel_bytes, name=default_file_name, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			await share.share_files([excel_file], text=default_file_name)
			page.run_task(Api.useractivity, username, f"Share Data KM Baku {search_input.value}")
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

	def close_dialog(e):
		page.pop_dialog()

	dialog_popup = ft.AlertDialog(
		title=ft.Text("Peringatan:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.YELLOW_600, text_align=ft.TextAlign.CENTER),
		content=ft.Text("Rute tidak boleh kosong...!!!", size=13, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
		actions=[ft.TextButton("Oke", on_click=close_dialog)],
		actions_alignment=ft.MainAxisAlignment.END
	)

	def input_change(e):
		kode = search_input.value.upper().strip()
		search_input.value = kode
		page.update()

	def search_click(e):
		kode = search_input.value.strip()
		if not kode:
			page.show_dialog(dialog_popup)
			status_text.value = ""
			daftar_konten.controls.clear()
			page.update()
			return None
		page.update()
		page.run_task(fetch_kmbaku, kode)

	search_input = ft.TextField(
		label=ft.Text("Rute", size=13),
		text_style=ft.TextStyle(color=ft.Colors.WHITE, size=13),
		border=ft.InputBorder.NONE,
		border_color=ft.Colors.GREY_400,
		prefix_icon=ft.Icons.ROUTE,
		cursor_color=ft.Colors.BLUE_400,
		autofocus=True,
		expand=True,
		on_change=input_change,
		on_submit=search_click
	)

	search_button = ft.IconButton(
		icon=ft.Icons.SEARCH,
		icon_color=ft.Colors.WHITE,
		icon_size=25,
		on_click=search_click
	)

	pencarian = ft.Container(
		content=ft.Row(
			controls=[search_input, search_button],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.CENTER
		),
		margin=ft.Margin(top=3)
	)

	btn_share = ft.Button(
		content=ft.Text("Share Data", size=13),
		width=333,
		style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
		icon=ft.Icons.SHARE,
		on_click=share_excel,
		visible=False
	)

	async def fetch_kmbaku(kode):
		daftar_konten.controls.clear()
		status_text.value = ""
		btn_share.visible = False
		loading_spinner.visible = True
		page.update()
		timeout = httpx.Timeout(120.0, connect=10.0)
		transport = httpx.AsyncHTTPTransport(retries=3)
		try:
			async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
				response = await client.post(
					url=config.MIKRO_API,
					headers=config.HEADERS,
					params={"page": "km_baku", "length": "-1", "search[value]": kode, "authorization": config.AUTHORIZATION}
				)
				if response.is_success:
					result = response.json()
					if result.get("data"):
						state_data["data_kmbaku"] = result["data"]
						status_text.value = (f"HASIL PENCARIAN : {result['recordsFiltered']}")
						status_text.color = ft.Colors.YELLOW_400
						status_text.size = 13
						for item in result["data"]:
							item_box = ft.Column(
								controls=[
									ft.Text(f"Rute: {item.get('rute')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Rute Layanan: {item.get('rute_layanan')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Nama Trip: {item.get('trip_name')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"KM Baku: {item.get('km_baku')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Keterangan: {item.get('keterangan')}", size=13, color=ft.Colors.WHITE),
									ft.Text(
										spans=[
											ft.TextSpan("Sumber :"),
											ft.TextSpan(
												text=item.get("sumber"),
												url=item.get("sumber"),
												style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, color=ft.Colors.BLUE_400)
											)
										],
										size=13,
										color=ft.Colors.WHITE
									),
									ft.Divider(thickness=0.5, color=ft.Colors.GREY_600)
								],
								spacing=0.5
							)
							daftar_konten.controls.append(item_box)
						btn_share.visible = True
						page.run_task(Api.useractivity, username, f"View KM Baku {kode}")
					else:
						DataFormatter.show_snackbar(page, "Data tidak ditemukan...!!!", "YELLOW_900")
						return None
				else:
					DataFormatter.show_snackbar(page, "Gagal mengambil data...!!!", "YELLOW_900")
					return None
		except httpx.TimeoutException:
			DataFormatter.show_snackbar(page, "Request timout error", "YELLOW_900")
			return None
		except Exception as err:
			DataFormatter.show_snackbar(page, f"{err}", "YELLOW_900")
			return None
		finally:
			loading_spinner.visible = False
			page.update()

	main_layout = ft.Stack(
		controls=[
			ft.Column(
				controls=[
					pencarian,
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