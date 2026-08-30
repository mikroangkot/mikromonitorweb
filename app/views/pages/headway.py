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

def build_excel(data_headway, list_dataunit, rute):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = [
		"Tanggal",
		"Lokasi",
		"TNKB",
		"Rute",
		"Odometer",
		"No. Bus",
		"Jam Mulai",
		"Jam Selesai",
		"Durasi",
		"Headway"
	]
	ws.append(headers)
	ws.freeze_panes = "A2"
	font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
	fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
	for col_num, header in enumerate(headers, 1):
		cell = ws.cell(row=1, column=col_num)
		cell.font = font_header
		cell.fill = fill_header
	total_data = len(data_headway)
	unit_map = {unit.get("no_body"): unit for unit in list_dataunit if unit.get("no_body")}
	for index, item in enumerate(data_headway):
		buscode = item.get("bus_code", "")
		formatted_buscode = buscode.replace("-", " ") if buscode else ""
		detail_unit = unit_map.get(formatted_buscode, {})
		rute_unit = detail_unit.get("rute")
		tnkb_unit = detail_unit.get("tnkb")
		durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
		headway_text = ""
		if index < total_data - 1:
			bus_berikutnya = data_headway[index + 1]
			headway_text = DataFormatter.hitung_durasi(item.get("start_time"), bus_berikutnya.get("start_time"))
		ws.append(
			[
				DataFormatter.format_tanggal(item.get("start_time")),
				DataFormatter.format_lokasi(item.get("dispatcher")),
				tnkb_unit,
				rute_unit,
				item.get("busodo"),
				formatted_buscode,
				DataFormatter.format_jam(item.get("start_time")),
				DataFormatter.format_jam(item.get("end_time")),
				durasi_perjalanan,
				headway_text
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
		if col_letter in ["A", "G", "H", "I", "J"]:
			for cell in col[1:]:
				cell.alignment = align_center_data
	excel_stream = io.BytesIO()
	wb.save(excel_stream)
	excel_stream.seek(0)
	return excel_stream.getvalue()

def headway_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"data_headway": [], "list_dataunit": []}
	status_text = ft.Text(value="")
	rekapan = ft.Container(content=ft.Row(controls=[status_text]))
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)
	share = ft.Share()
	pengendapan = []
	storage = DataFormatter()

	async def share_excel(e):
		if not state_data["data_headway"]:
			DataFormatter.show_snackbar(page, "Tidak ada data untuk di export...!!!", "YELLOW_900")
			return None
		btn_share.disabled = True
		btn_share.icon = None
		btn_share.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		dispatcher = search_input.value.split("/")
		rute = dispatcher[1].strip()
		dispatcher_lokasi = dispatcher[0].split("_")
		lokasi = dispatcher_lokasi[1].strip()
		default_file_name = f"Data Headway {DataFormatter.format_rute(rute)} Lokasi {lokasi} {datetime.now().strftime('%Y%m%d')}.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["data_headway"], state_data["list_dataunit"], rute)
			excel_file = ft.ShareFile.from_bytes(excel_bytes, name=default_file_name, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			await share.share_files([excel_file], text=default_file_name)
			page.run_task(Api.useractivity, username, f"Share Data Headway {DataFormatter.format_rute(rute)} Lokasi {lokasi} Periode: {datetime.now().strftime('%d-%m-%Y')} s/d {datetime.now().strftime('%d-%m-%Y')}")
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
		content=ft.Text("Masukkan Lokasi/Rute terlebih dahulu!", size=13, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
		actions=[ft.TextButton("Oke", on_click=close_dialog)],
		actions_alignment=ft.MainAxisAlignment.END
	)

	async def open_search_view(e):
		if hasattr(search_input, "open_view_async"):
			await search_input.open_view_async()
		else:
			await search_input.open_view()

	async def select_pengendapan(e):
		selected_value = e.control.data
		search_input.value = selected_value
		if hasattr(search_input, "close_view_async"):
			await search_input.close_view_async(selected_value)
		else:
			await search_input.close_view(selected_value)
		page.update()
		page.run_task(fetch_headway, selected_value)

	def populate_search_controls(filter_text=""):
		filtered = [
			b for b in pengendapan
			if filter_text.upper() in b.upper()
		] if filter_text else pengendapan

		search_input.controls = [
			ft.ListTile(
				title=ft.Text(entry),
				data=entry,
				on_click=select_pengendapan
			) for entry in filtered[:50]
		]

	async def handle_change(e):
		val = e.data.upper() if e.data else ""
		populate_search_controls(val)
		search_input.update()
		if val:
			if hasattr(search_input, "open_view_async"):
				await search_input.open_view_async()
			else:
				await search_input.open_view()

	async def search_click(e):
		entry = search_input.value.strip().upper() if search_input.value else ""
		if not entry:
			page.show_dialog(dialog_popup)
			status_text.value = ""
			daftar_konten.controls.clear()
			page.update()
			return None
		if hasattr(search_input, "close_view_async"):
			await search_input.close_view_async(entry)
		else:
			page.run_task(search_input.close_view, entry)
		page.update()
		page.run_task(fetch_headway, entry)

	search_input = ft.SearchBar(
		bar_hint_text="Cari Pengendapan...",
		view_hint_text="Ketik Lokasi Pengendapan...",
		bar_text_style=ft.TextStyle(color=ft.Colors.GREY_400, size=13),
		bar_leading=ft.Icon(ft.Icons.AV_TIMER, color=ft.Colors.GREY_400),
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
			controls=[search_input, search_button],
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

	async def fetch_lokasi():
		nonlocal pengendapan
		try:
			timeout = httpx.Timeout(20.0, connect=10.0)
			transport = httpx.AsyncHTTPTransport(retries=3)
			async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
				response = await client.get(config.LOKASI_HEADWAY)
				if response.is_success:
					result = response.json()
					endapan = []
					for item in result:
						if isinstance(item, dict) and "area" in item and item["area"]:
							parts = item["area"].split("/")
							wilayah = f"{parts[0].strip()}/{parts[1].strip()}"
							endapan.append(wilayah)
					pengendapan = sorted(list(set(endapan)), key=str.lower)
					populate_search_controls()
					search_input.update()
					page.update()
		except Exception as err:
			DataFormatter.log_msg(err)

	page.run_task(fetch_lokasi)

	async def fetch_headway(input_value: str):
		daftar_konten.controls.clear()
		status_text.value = ""
		btn_share.visible = False
		loading_spinner.visible = True
		page.update()
		if "/" not in input_value:
			loading_spinner.visible = False
			DataFormatter.show_snackbar(page, "Gunakan format: Lokasi/Rute", "YELLOW_900")
			page.update()
			return None
		parts = input_value.split("/")
		dispatcher = parts[0].strip()
		rute = parts[1].strip()
		lokasi_awal = dispatcher.split("_")
		lokasi = lokasi_awal[1].strip()
		timeout = httpx.Timeout(120.0, connect=10.0)
		transport = httpx.AsyncHTTPTransport(retries=3)
		try:
			async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
				response = await client.get(
					url=config.HISTORY_HEADWAY,
					headers=config.HEADERS,
					params={"dispatcher": dispatcher, "rute": rute}
				)
				if response.is_success:
					result = response.json()
					if result.get("success") == 1 and result.get("getdata"):
						state_data["data_headway"] = result["getdata"]
						total_data = len(result["getdata"])
						bus_unik = set(item.get("bus_code") for item in result["getdata"] if item.get("bus_code"))
						total_unit = len(bus_unik)
						status_text.value = (f"TOTAL UNIT : {total_unit}    ||    TOTAL DATA : {total_data}")
						status_text.color = ft.Colors.YELLOW_400
						status_text.size = 13
						list_dataunit = await storage.get("dataunit") or []
						state_data["list_dataunit"] = list_dataunit
						unit_map = {unit.get("no_body"): unit for unit in list_dataunit if unit.get("no_body")}
						for index, item in enumerate(result["getdata"]):
							buscode = item.get("bus_code", "")
							formatted_buscode = buscode.replace("-", " ") if buscode else ""
							detail_unit = unit_map.get(formatted_buscode, {})
							rute_unit = detail_unit.get("rute", "-")
							tnkb_unit = detail_unit.get("tnkb", "-")
							durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
							headway_text = "-"
							if index < total_data - 1:
								bus_berikutnya = result["getdata"][index + 1]
								headway_text = DataFormatter.hitung_durasi(item.get("start_time"), bus_berikutnya.get("start_time"))
							item_box = ft.Column(
								controls=[
									ft.Text(f"Tanggal: {DataFormatter.format_tanggal(item.get('start_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Lokasi: {DataFormatter.format_lokasi(dispatcher)}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"TNKB: {tnkb_unit}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Rute: {rute_unit}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Odometer: {item.get('busodo')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"No. Bus: {formatted_buscode}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Jam Mulai: {DataFormatter.format_jam(item.get('start_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Jam Selesai: {DataFormatter.format_jam(item.get('end_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Durasi: {durasi_perjalanan}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Headway: {headway_text}", size=13, color=ft.Colors.WHITE),
									ft.Divider(thickness=0.5, color=ft.Colors.GREY_600)
								],
								spacing=0.5
							)
							daftar_konten.controls.append(item_box)
						btn_share.visible = True
						page.run_task(Api.useractivity, username, f"View Headway Rute {DataFormatter.format_rute(rute)} Lokasi {lokasi} Periode: {datetime.now().strftime('%d-%m-%Y')} s/d {datetime.now().strftime('%d-%m-%Y')}")
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
			DataFormatter.show_snackbar(page, f"Server error: {err}", "YELLOW_900")
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