import re

class FormatDispatcher:

	@staticmethod
	def format_dispatcher(text):
		clean = str(text).upper()
		clean = re.sub(r"[^A-Z0-9]", "", clean)
		match = re.match(r"^([A-Z]+)(\d+)$", clean)
		if match:
			huruf = match.group(1)
			angka = match.group(2)
			return f"{huruf}-{angka}"
		return text
