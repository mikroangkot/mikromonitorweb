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

def build_excel(data_unit, list_kmbaku):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = ["No. Body", "Rute", "Rute Layanan", "TNKB", "TH Reg", "Jenis Kendaraan", "Tahapan", "Kontrak"]
	ws.append(headers)
	ws.freeze_panes = "A2"
	font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
	fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
	for col_num, header in enumerate(headers, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.font = font_header
		cell.fill = fill_header
	km_map = {km.get("rute"): km for km in list_kmbaku if km.get("rute")}
	for index, item in enumerate(data_unit):
		detail_km = km_map.get(item.get("rute"), {})
		rutelayanan = detail_km.get("rute_layanan")
		ws.append(
			[
				item.get("no_body"),
				item.get("rute"),
				rutelayanan,
				item.get("tnkb"),
				item.get("th_registrasi"),
				item.get("jenis_kendaraan"),
				item.get("tahapan"),
				item.get("kontrak")
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

def unit_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"data_unit": [], "data_kmbaku": []}
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)
	share = ft.Share()
	storage = DataFormatter()

	async def share_excel(e):
		if not state_data["data_unit"]:
			DataFormatter.show_snackbar(page, "Tidak ada data...!!!", "YELLOW_900")
			return None
		btn_share.disabled = True
		btn_share.icon = None
		btn_share.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		default_file_name = f"Data Unit {search_input.value}.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["data_unit"], state_data["data_kmbaku"])
			excel_file = ft.ShareFile.from_bytes(excel_bytes, name=default_file_name, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			await share.share_files([excel_file], text=default_file_name)
			page.run_task(Api.useractivity, username, f"Share Data Unit {search_input.value}")
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
		content=ft.Text("Data tidak boleh kosong...!!!", size=13, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
		actions=[ft.TextButton("Oke", on_click=close_dialog)],
		actions_alignment=ft.MainAxisAlignment.END
	)

	def input_change(e):
		pencarian_input = search_input.value.upper()
		search_input.value = pencarian_input
		page.update()

	def search_click(e):
		pencarian_input = search_input.value.strip()
		if not pencarian_input:
			page.show_dialog(dialog_popup)
			rekapan.visible = False
			daftar_konten.controls.clear()
			page.update()
			return None
		page.update()
		page.run_task(muat_data, pencarian_input)

	search_input = ft.TextField(
		label=ft.Text("No. Bus / Rute", size=13),
		text_style=ft.TextStyle(color=ft.Colors.WHITE, size=13),
		border=ft.NoInputBorder(),
		prefix_icon=ft.Icons.DIRECTIONS_BUS,
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
									ft.Container(
										content=ft.Icon(ft.Icons.SEARCH, size=25, color=ft.Colors.YELLOW_400),
										padding=ft.Padding(top=6, bottom=6),
										border_radius=8
									),
									ft.Column(
										controls=[
											ft.Text("HASIL PENCARIAN :", size=13, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
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
		margin=ft.Margin(top=-15, bottom=0),
		visible=False
	)

	async def muat_data(pencarian_input):
		daftar_konten.controls.clear()
		rekapan.visible = False
		btn_share.visible = False
		loading_spinner.visible = True
		page.update()
		try:
			result = await storage.get("dataunit") or []
			raw_data = result
			list_kmbaku = await storage.get("datakmbaku") or []
			state_data["data_kmbaku"] = list_kmbaku
			km_map = {km.get("rute"): km for km in list_kmbaku if km.get("rute")}
			enriched_raw_data = []
			for item in raw_data:
				item_copy = dict(item)
				detail_km = km_map.get(item.get("rute"), {})
				item_copy["rute_layanan_copy"] = detail_km.get("rute_layanan")
				enriched_raw_data.append(item_copy)
			query = (pencarian_input or "").strip().lower()
			if query:
				filtered_data = []
				for item in enriched_raw_data:
					rute = str(item.get("rute") or "").lower()
					no_body = str(item.get("no_body") or "").lower()
					if query in rute or query in no_body:
						filtered_data.append(item)
			else:
				filtered_data = enriched_raw_data
			state_data["data_unit"] = filtered_data
			total_data = f"{len(filtered_data):,}".replace(",", ".")
			if len(filtered_data) == 0:
				DataFormatter.show_snackbar(page, "Data Tidak Ditemukan...", "YELLOW_900")
				return None
			for index, item in enumerate(state_data["data_unit"][:50]):
				rutelayanan = item.get("rute_layanan_copy", "-")
				item_box = ft.Column(
					controls=[
						ft.Text(f"No. Body: {item.get('no_body')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Rute: {item.get('rute')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Rute Layanan: {rutelayanan}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"TNKB: {item.get('tnkb')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"TH Registrasi: {item.get('th_registrasi')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Jenis Kendaraan: {item.get('jenis_kendaraan')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Tahapan: {item.get('tahapan')}", size=13, color=ft.Colors.WHITE),
						ft.Text(f"Kontrak: {item.get('kontrak')}", size=13, color=ft.Colors.WHITE),
						ft.Text(
							spans=[ft.TextSpan("Sumber :"), ft.TextSpan(text=item.get("file"), url=item.get("file"), style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, color=ft.Colors.BLUE_400))],
							size=13,
							color=ft.Colors.WHITE
						),
						ft.Divider(thickness=0.5, color=ft.Colors.GREY_600)
					],
					spacing=0.5
				)
				daftar_konten.controls.append(item_box)
			hasil_pencarian.value = total_data
			rekapan.visible = True
			btn_share.visible = True
			page.run_task(Api.useractivity, username, f"View Data Unit {pencarian_input}")
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
