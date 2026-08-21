from datetime import datetime

class FormatDatetime:

	@staticmethod
	def format_tanggal(tanggal):
		if not tanggal:
			return "-"
		default = str(tanggal)[:10]
		try:
			tanggal_obj = datetime.strptime(default, "%Y-%m-%d")
			return tanggal_obj.strftime("%d-%m-%Y")
		except ValueError:
			return default

	@staticmethod
	def format_jam(jam):
		if not jam:
			return "-"
		try:
			jam_obj = datetime.strptime(str(jam).split(".")[0], "%Y-%m-%d %H:%M:%S")
			return jam_obj.strftime("%H:%M:%S")
		except ValueError:
			return str(jam)[11:16] if len(str(jam)) >= 16 else "-"

	@staticmethod
	def hitung_durasi(start, end):
		if not start or not end:
			return "00:00:00"
		try:
			start_time = datetime.fromisoformat(start.replace("Z", "").replace(" ", "T"))
			end_time = datetime.fromisoformat(end.replace("Z", "").replace(" ", "T"))
			selisih = end_time - start_time
			total_detik = int(selisih.total_second())
			if total_detik < 0:
				return "00:00:00"
			jam = total_detik // 3600
			menit = (total_detik % 3600) // 60
			detik = total_detik % 60
			return f"{jam:02d}:{menit:02d}:{detik:02d}"
		except Exception:
			return "00:00:00"