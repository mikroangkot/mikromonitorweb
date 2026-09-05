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

def build_excel(data_history, list_dataunit):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = [
		"Tanggal",
		"ID Order",
		"Pramudi",
		"Lokasi",
		"TNKB",
		"Rute",
		"No. Bus",
		"Jam Mulai",
		"Jam Selesai",
		"Durasi",
		"Nama Trip Perjalanan",
		"KM Baku",
		"Odometer",
		"Nama Petugas"
	]
	ws.append(headers)
	ws.freeze_panes = "A2"
	font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
	fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
	for col_num, header in enumerate(headers, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.font = font_header
		cell.fill = fill_header
	unit_map = {unit.get("no_body"): unit for unit in list_dataunit if unit.get("no_body")}
	for index, item in enumerate(data_history):
		buscode = item.get("bus_code", "")
		formatted_buscode = buscode.replace("-", " ") if buscode else ""
		detail_unit = unit_map.get(formatted_buscode, {})
		rute_unit = detail_unit.get("rute")
		tnkb_unit = detail_unit.get("tnkb")
		pramudi = str(item.get("driver_id")).replace(",", " - ").upper()
		trip_name = str(item.get("trip_desc")).replace(">>", "-").replace(">", "-")
		nama_petugas = f"{item.get('nama')} - [{item.get('updateby')}]".upper()
		try:
			kmbaku = float(item.get("kmisi", 0))
			odometer = float(item.get("busodo", 0))
		except (ValueError, TypeError):
			kmbaku = 0.0
			odometer = 0
		durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
		ws.append(
			[
				DataFormatter.format_tanggal(item.get("start_time")),
				item.get("do_id"),
				pramudi,
				DataFormatter.format_lokasi(item.get("dispatcher")),
				tnkb_unit,
				rute_unit,
				formatted_buscode,
				DataFormatter.format_jam(item.get("start_time")),
				DataFormatter.format_jam(item.get("end_time")),
				durasi_perjalanan,
				trip_name,
				kmbaku,
				odometer,
				nama_petugas
			]
		)
		ws.cell(row=ws.max_row, column=12).number_format = "#,##0.####"
	kolom_terakhir = openpyxl.utils.get_column_letter(len(headers))
	baris_terakhir = ws.max_row
	ws.auto_filter.ref = f"A1:{kolom_terakhir}{baris_terakhir}"
	align_center_data = Alignment(horizontal="center", vertical="center")
	for col in ws.columns:
		max_len = max(len(str(cell.value or "")) for cell in col)
		col_letter = openpyxl.utils.get_column_letter(col[0].column)
		ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
		if col_letter in ["A", "H", "I", "J"]:
			for cell in col[1:]:
				cell.alignment = align_center_data
	excel_stream = io.BytesIO()
	wb.save(excel_stream)
	excel_stream.seek(0)
	return excel_stream.getvalue()

def history_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"data_history": [], "list_dataunit": []}
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)
	share = ft.Share()
	raw_bus_data = []
	storage = DataFormatter()

	async def share_excel(e):
		if not state_data["data_history"]:
			DataFormatter.show_snackbar(page, "Tidak ada data untuk di export...!!!", "YELLOW_900")
			return None
		btn_share.disabled = True
		btn_share.icon = None
		btn_share.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		default_file_name = f"Data History Bus {pencarian_input.value.replace('-', ' ')} {datetime.now().strftime('%Y%m%d')}.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["data_history"], state_data["list_dataunit"])
			excel_file = ft.ShareFile.from_bytes(excel_bytes, name=default_file_name, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			await share.share_files([excel_file], text=default_file_name)
			page.run_task(Api.useractivity, username, f"Share Data History Bus {pencarian_input.value.replace('-', ' ')} Periode: {datetime.now().strftime('%d-%m-%Y')} s/d {datetime.now().strftime('%d-%m-%Y')}")
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
		content=ft.Text("Kode Bus tidak boleh kosong...!!!", size=13, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
		actions=[ft.TextButton("Oke", on_click=close_dialog)],
		actions_alignment=ft.MainAxisAlignment.END
	)

	async def open_search_view(e):
		if hasattr(pencarian_input, "open_view_async"):
			await pencarian_input.open_view_async()
		else:
			await pencarian_input.open_view()

	async def select_bus(e):
		selected_value = e.control.data
		pencarian_input.value = selected_value
		if hasattr(pencarian_input, "close_view_async"):
			await pencarian_input.close_view_async(selected_value)
		else:
			await pencarian_input.close_view(selected_value)
		page.update()
		page.run_task(fetch_history, selected_value)

	def populate_search_controls(filter_text=""):
		filtered = [
			b for b in raw_bus_data
			if filter_text.upper() in b.upper()
		] if filter_text else raw_bus_data

		pencarian_input.controls = [
			ft.ListTile(
				title=ft.Text(buscode),
				data=buscode,
				on_click=select_bus
			) for buscode in filtered[:50]
		]

	async def handle_change(e):
		val = e.data.upper() if e.data else ""
		populate_search_controls(val)
		pencarian_input.update()
		if val:
			if hasattr(pencarian_input, "open_view_async"):
				await pencarian_input.open_view_async()
			else:
				await pencarian_input.open_view()

	async def search_click(e):
		buscode = pencarian_input.value.strip().upper() if pencarian_input.value else ""
		if not buscode:
			page.show_dialog(dialog_popup)
			rekapan.visible = False
			daftar_konten.controls.clear()
			page.update()
			return None
		if hasattr(pencarian_input, "close_view_async"):
			await pencarian_input.close_view_async(buscode)
		else:
			page.run_task(pencarian_input.close_view, buscode)
		page.update()
		page.run_task(fetch_history, buscode)

	pencarian_input = ft.SearchBar(
		bar_hint_text="Cari Bus...",
		view_hint_text="Ketik Kode Bus...",
		bar_text_style=ft.TextStyle(color=ft.Colors.GREY_400, size=13),
		bar_leading=ft.Icon(ft.Icons.DIRECTIONS_BUS, color=ft.Colors.GREY_400),
		bar_shadow_color=ft.Colors.BLUE_400,
		bar_bgcolor=ft.Colors.TRANSPARENT,
		bar_overlay_color=ft.Colors.TRANSPARENT,
		bar_border_side=ft.BorderSide(width=0, color=ft.Colors.TRANSPARENT),
		autofocus=True,
		bar_elevation=0,
		controls=[],
		expand=True,
		on_change=handle_change,
		on_submit=search_click,
		on_tap=open_search_view
	)

	search_button = ft.IconButton(
		icon=ft.Icons.SEARCH,
		icon_color=ft.Colors.WHITE,
		icon_size=25,
		on_click=search_click
	)

	pencarian = ft.Container(
		content=ft.Row(
			controls=[pencarian_input, search_button],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.CENTER
		),
		margin=ft.Margin(top=-1)
	)

	btn_share = ft.Button(
		content=ft.Text("Share Data", size=13),
		width=333,
		style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
		icon=ft.Icons.SHARE,
		on_click=share_excel,
		visible=False
	)

	total_trip_val = ft.Text("0", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW_400)
	total_kmtempuh_val = ft.Text("0", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)
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
										content=ft.Icon(ft.Icons.DIRECTIONS_BUS, size=25, color=ft.Colors.YELLOW_400),
										padding=ft.Padding(top=6, bottom=6),
										border_radius=8
									),
									ft.Column(
										controls=[
											ft.Text("TOTAL TRIP :", size=13, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
											total_trip_val
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
				),
				ft.Container(
					expand=True,
					content=ft.Card(
						content=ft.Container(
							content=ft.Row(
								controls=[
									ft.Container(
										content=ft.Icon(ft.Icons.ANALYTICS, size=25, color=ft.Colors.BLUE_300),
										padding=ft.Padding(top=6, bottom=6),
										border_radius=8
									),
									ft.Column(
										controls=[
											ft.Text("KM TEMPUH :", size=13, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
											total_kmtempuh_val
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

	async def cari_bus():
		nonlocal raw_bus_data
		try:
			timeout = httpx.Timeout(20.0, connect=10.0)
			transport = httpx.AsyncHTTPTransport(retries=3)
			async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
				response = await client.get(config.LIST_BUS)
				if response.is_success:
					result = response.json()
					bus_list = []
					for item in result:
						if isinstance(item, dict) and "bus" in item and item["bus"]:
							parts = item["bus"].split(" / ")
							buscode = parts[0].strip()
							bus_list.append(buscode)
					raw_bus_data = sorted(list(set(bus_list)), key=str.lower)
					populate_search_controls()
					pencarian_input.update()
					page.update()
		except Exception as err:
			DataFormatter.log_msg(err)

	page.run_task(cari_bus)

	async def fetch_history(buscode):
		daftar_konten.controls.clear()
		rekapan.visible = False
		btn_share.visible = False
		loading_spinner.visible = True
		page.update()
		timeout = httpx.Timeout(180.0, connect=10.0)
		transport = httpx.AsyncHTTPTransport(retries=3)
		try:
			async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
				response = await client.get(
					url=config.HISTORY_BUS,
					headers=config.HEADERS,
					params={"bus_code": buscode}
				)
				if response.is_success:
					result = response.json()
					if result.get("success") == 1 and result.get("getdata"):
						state_data["data_history"] = result["getdata"]
						list_dataunit = await storage.get("dataunit") or []
						state_data["list_dataunit"] = list_dataunit
						unit_map = {unit.get("no_body"): unit for unit in list_dataunit if unit.get("no_body")}
						total_trip = 0
						total_kmtempuh = 0.0
						for item in result["getdata"]:
							buscode = item.get("bus_code")
							formatted_buscode = buscode.replace("-", " ") if buscode else ""
							detail_unit = unit_map.get(formatted_buscode, {})
							rute_unit = detail_unit.get("rute", "-")
							tnkb_unit = detail_unit.get("tnkb", "-")
							durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
							kmbaku = item.get("kmisi")
							try:
								kmbaku_value = float(kmbaku)
							except(ValueError, TypeError):
								kmbaku_value = 0.0
							if kmbaku_value > 0:
								total_trip += 1
							total_kmtempuh += kmbaku_value
							pramudi = str(item.get("driver_id")).replace(",", " - ").upper()
							trip_name = str(item.get("trip_desc")).replace(">>", "-").replace(">", "-")
							petugas = f"{item.get('nama')} - [{item.get('updateby')}]"
							item_box = ft.Column(
								controls=[
									ft.Text(f"Tanggal: {DataFormatter.format_tanggal(item.get('start_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"ID Order: {item.get('do_id')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Pramudi: {pramudi}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Lokasi: {DataFormatter.format_lokasi(item.get('dispatcher'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"TNKB: {tnkb_unit}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Rute: {rute_unit}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"No. Bus: {item.get('bus_code').replace('-', ' ')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Jam Mulai: {DataFormatter.format_jam(item.get('start_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Jam Selesai: {DataFormatter.format_jam(item.get('end_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Durasi: {durasi_perjalanan}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Nama Trip: {trip_name}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"KM Baku: {item.get('kmisi')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Odometer: {item.get('busodo')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Petugas: {petugas}", size=13, color=ft.Colors.WHITE),
									ft.Divider(thickness=0.5, color=ft.Colors.GREY_600)
								],
								spacing=0.5
							)
							daftar_konten.controls.append(item_box)
						total_trip_val.value = total_trip
						total_kmtempuh_val.value = f"{round(total_kmtempuh, 4):g}"
						rekapan.visible = True
						btn_share.visible = True
						page.run_task(Api.useractivity, username, f"View History Bus {item.get('bus_code').replace('-', ' ')} Periode: {datetime.now().strftime('%d-%m-%Y')} s/d {datetime.now().strftime('%d-%m-%Y')}")
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
			DataFormatter.show_snackbar(page, f"Internal Server Error: {err}", "YELLOW_900")
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
