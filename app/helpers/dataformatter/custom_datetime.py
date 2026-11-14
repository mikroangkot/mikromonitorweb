from datetime import datetime
from zoneinfo import ZoneInfo

class FormatDatetime:

	@staticmethod
	def format_tanggal(tanggal):
		if not tanggal:
			return "00-00-0000"
		default = str(tanggal)[:10]
		try:
			tanggal_obj = datetime.strptime(default, "%Y-%m-%d")
			return tanggal_obj.strftime("%d-%m-%Y")
		except ValueError:
			return default

	@staticmethod
	def format_jam(jam):
		if not jam:
			return "00:00:00"
		try:
			jam_obj = datetime.strptime(str(jam).split(".")[0], "%Y-%m-%d %H:%M:%S")
			return jam_obj.strftime("%H:%M:%S")
		except ValueError:
			return str(jam)[11:19] if len(str(jam)) >= 19 else "00:00:00"

	@staticmethod
	def hitung_durasi(start, end):
		if not start or not end:
			return "00:00:00"
		try:
			start_time = datetime.fromisoformat(start.replace("Z", "").replace(" ", "T"))
			end_time = datetime.fromisoformat(end.replace("Z", "").replace(" ", "T"))
			selisih = end_time - start_time
			total_detik = int(selisih.total_seconds())
			if total_detik < 0:
				return "00:00:00"
			jam = total_detik // 3600
			menit = (total_detik % 3600) // 60
			detik = total_detik % 60
			return f"{jam:02d}:{menit:02d}:{detik:02d}"
		except Exception:
			return "00:00:00"

	@staticmethod
	def datetime_indo(dt_obj):
		if not dt_obj:
			return '00-00-0000 00:00:00'
		wib_tz = ZoneInfo('Asia/Jakarta')
		dt_wib = dt_obj.astimezone(wib_tz)
		hari = {
			0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis',
			4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
		}
		bulan = {
			1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
			7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
		}
		nama_hari = hari[dt_wib.weekday()]
		tanggal = dt_wib.day
		nama_bulan = bulan[dt_wib.month]
		tahun = dt_wib.year
		jam = dt_wib.strftime('%H:%M:%S')
		return f'{nama_hari}, {tanggal} {nama_bulan} {tahun} {jam} WIB'

	@staticmethod
	def format_tanggal(dt_str):
		if not dt_str:
			return '00-00-0000'
		tanggal_raw = str(dt_str)[:10]
		try:
			dt_obj = datetime.strptime(tanggal_raw, '%Y-%m-%d')
			return dt_obj.strftime('%d-%m-%Y')
		except ValueError:
			return tanggal_raw

	@staticmethod
	def format_tanggal_hari(dt_str):
		if not dt_str:
			return '00-00-0000'
		tanggal_raw = str(dt_str)[:19]
		try:
			dt_obj = datetime.strptime(tanggal_raw, '%d-%m-%Y %H:%M:%S')
			hari = {
				0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis',
				4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
			}
			bulan = {
				1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
				7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
			}
			nama_hari = hari.get(dt_obj.weekday(), '')
			tanggal = dt_obj.day
			nama_bulan = bulan[dt_obj.month]
			tahun = dt_obj.year
			return f"{nama_hari}, {tanggal} {nama_bulan} {tahun}"
		except ValueError:
			return tanggal_raw

	@staticmethod
	def format_tanggal_komplit(dt_str):
		if not dt_str:
			return '00-00-0000 00:00:00'
		tanggal_raw = str(dt_str)[:19]
		try:
			dt_obj = datetime.strptime(tanggal_raw, '%d-%m-%Y %H:%M:%S')
			hari = {
				0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis',
				4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
			}
			bulan = {
				1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
				7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
			}
			nama_hari = hari.get(dt_obj.weekday(), '')
			tanggal = dt_obj.day
			nama_bulan = bulan[dt_obj.month]
			tahun = dt_obj.year
			jam = dt_obj.strftime('%H:%M:%S')
			return f"{nama_hari}, {tanggal} {nama_bulan} {tahun} {jam} WIB"
		except ValueError:
			return tanggal_raw

	@staticmethod
	def format_jam(dt_str):
		if not dt_str:
			return '00:00:00'
		try:
			dt_obj = datetime.strptime(str(dt_str).split('.')[0], '%d-%m-%Y %H:%M:%S')
			return f"{dt_obj.strftime('%H:%M:%S')} WIB"
		except ValueError:
			return str(dt_str[11:16] if len(str(dt_str)) >= 16 else '-')