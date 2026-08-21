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

def build_excel(data_history):
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Data"
	headers = [
		"Tanggal",
		"ID Order",
		"Pramudi",
		"Lokasi",
		"Rute",
		"No. Bus",
		"Jam Mulai",
		"Jam Selesai",
		"Durasi",
		"Nama Trip Perjalanan",
		"KM Baku",
		"Odometer Bus",
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
	for index, item in enumerate(data_history):
		pramudi = str(item.get("driver_id")).replace(",", " - ").upper()
		trip_name = str(item.get("trip_desc")).replace(">>", "-").replace(">", "-")
		nama_petugas = f"{item.get("nama")} - [{item.get("updateby")}]".upper()
		durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
		buscode = item.get("bus_code").replace("-", " ").strip().upper()
		ws.append(
			[
				DataFormatter.format_tanggal(item.get("start_time")),
				item.get("do_id"),
				pramudi,
				item.get("dispatcher"),
				item.get("koridor"),
				buscode,
				DataFormatter.format_jam(item.get("start_time")),
				DataFormatter.format_jam(item.get("end_time")),
				durasi_perjalanan,
				trip_name,
				item.get("kmisi"),
				item.get("busodo"),
				nama_petugas
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
		if col_letter in ["A", "G", "H", "I"]:
			for cell in col[1:]:
				cell.alignment = align_center_data
	excel_stream = io.BytesIO()
	wb.save(excel_stream)
	excel_stream.seek(0)
	return excel_stream.getvalue()

def history_view(page: ft.Page):
	profile = page.session.store.get("current_user")
	username = profile.get("nama", "-")
	state_data = {"data_history": []}
	daftar_konten = ft.ListView(spacing=1, padding=1, expand=True)

	async def export_excel(e):
		if not state_data["data_history"]:
			DataFormatter.show_snackbar(page, "Tidak ada data untuk di export...!!!", "YELLOW_900")
			return None
		btn_export.disable = True
		btn_export.icon = None
		btn_export.content = ft.ProgressRing(width=15, height=15, color=ft.Colors.YELLOW_400)
		page.update()
		await asyncio.sleep(0.1)
		default_file_name = f"History {search_input.value} {datetime.now().strftime('%Y%m%d')}.xlsx"
		try:
			excel_bytes = await asyncio.to_thread(build_excel, state_data["data_history"])
			save_path = await ft.FilePicker().save_file(
				dialog_title="Save to Excel",
				file_name=default_file_name,
				file_type=ft.FilePickerFileType.CUSTOM,
				allowed_extensions=["xlsx"],
				src_bytes=excel_bytes
			)
			if save_path:
				DataFormatter.show_snackbar(page, "Data berhasil disimpan...!!!", "GREEN_900")
				btn_export.visible = False
			else:
				DataFormatter.show_snackbar(page, "Penyimpanan dibatalkan...!!!", "YELLOW_900")
		except Exception as err:
			DataFormatter.show_snackbar(page, f"Gagal menyimpan file: {err}", "YELLOW_900")
		btn_export.disabled = False
		btn_export.icon = ft.Icons.SAVE_AS
		btn_export.content = ft.Text("Export to Excel")
		page.update()

	api_result_container = ft.Column(
		controls=[daftar_konten],
		scroll=ft.ScrollMode.AUTO,
		horizontal_alignment=ft.CrossAxisAlignment.START,
		alignment=ft.MainAxisAlignment.START,
		expand=True
	)

	status_text = ft.Text(value="")
	rekapan = ft.Container(content=ft.Row(controls=[status_text]))

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

	def input_change(e):
		buscode = search_input.value.upper().strip()
		search_input.value = DataFormatter.format_dispatcher(buscode)
		page.update()

	def search_click(e):
		buscode = search_input.value.strip()
		if not buscode:
			page.show_dialog(dialog_popup)
			status_text.value = ""
			daftar_konten.controls.clear()
			page.update()
			return None
		page.update()
		page.run_task(fetch_history, buscode)

	search_input = ft.TextField(
		label=ft.Text("Kode Bus:", size=13),
		text_style=ft.TextStyle(color=ft.Colors.WHITE, size=13),
		border=ft.InputBorder.NONE,
		border_color=ft.Colors.GREY_400,
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

	search_bar = ft.Container(
		ft.Row(
			controls=[search_input, search_button],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.CENTER,
			margin=ft.Margin(top=3)
		)
	)

	btn_export = ft.Button(
		content=ft.Text("Export to Excel", size=13),
		width=310,
		style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
		icon=ft.Icons.SAVE_AS,
		on_click=export_excel,
		visible=False
	)

	async def fetch_history(buscode):
		daftar_konten.controls.clear()
		status_text.value = ""
		btn_export.visible = False
		loading_spinner.visible = True
		page.update()

		timeout = httpx.Timeout(120.0, connect=10.0)

		try:
			async with httpx.AsyncClient(timeout=timeout) as client:
				response = await client.get(
					url=config.HISTORY_BUS,
					headers=config.HEADERS,
					params={"bus_code": buscode}
				)
				if response.is_success:
					result = response.json()
					if result.get("success") == 1 and result.get("getdata"):
						state_data["data_history"] = result["getdata"]
						total_trip = 0
						total_kmtempuh = 0.0
						for item in result["getdata"]:
							durasi_perjalanan = DataFormatter.hitung_durasi(item.get("start_time"), item.get("end_time"))
							kmbaku = item.get("kmisi")
							try:
								kmbaku_value = float(kmbaku)
							except(ValueError, TypeError):
								kmbaku_value = 0.0
							if kmbaku_value > 0:
								total_trip += 1
							total_kmtempuh += kmbaku_value
							status_text.value = (f"TOTAL TRIP : {total_trip}    ||    TOTAL KM TEMPUH : {total_kmtempuh:.1f}")
							status_text.color = ft.Colors.YELLOW_400
							status_text.size = 13

							pramudi = str(item.get("driver_id")).replace(",", " - ").upper()
							trip_name = str(item.get("trip_desc")).replace(">>", "-").replace(">", "-")
							petugas = f"{item.get('nama')} - [{item.get('updateby')}]"
							item_box = ft.Column(
								controls=[
									ft.Text(f"Tanggal: {DataFormatter.format_tanggal(item.get('start_time'))}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"ID Order: {item.get('do_id')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Pramudi: {pramudi}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Lokasi: {item.get('dispatcher')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"Rute: {item.get('koridor')}", size=13, color=ft.Colors.WHITE),
									ft.Text(f"No. Bus: {item.get('bus_code')}", size=13, color=ft.Colors.WHITE),
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
						btn_export.visible = True
						page.run_task(Api.useractivity, username, f"History Bus {item.get('bus_code')} Periode: {datetime.now().strftime('%d-%m-%Y')} s/d {datetime.now().strftime('%d-%m-%Y')}")
					else:
						DataFormatter.show_snackbar(page, "Data tidak ditemukan...!!!", "YELLOW_900")
						return None
				else:
					DataFormatter.show_snackbar(page, "Gagal mengambil data...!!!", "YELLOW_900")
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
					search_bar,
					rekapan,
					ft.Container(content=api_result_container, expand=True),
					btn_export
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