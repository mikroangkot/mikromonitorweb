import re

class FormatDispatcher:

	@staticmethod
	def format_lokasi(text):
		parts = text.split("_")
		lokasi = parts[1].strip()
		return lokasi

	@staticmethod
	def format_rute(text):
		clean = str(text).upper()
		clean = re.sub(r"[^A-Z0-9]", "", clean)
		match = re.match(r"^([A-Z]+)(\d+)$", clean)
		if match:
			huruf = match.group(1)
			angka = int(match.group(2))
			return f"{huruf}.{angka:02d}"
		return text