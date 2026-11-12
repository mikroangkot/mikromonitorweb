from datetime import datetime
from zoneinfo import ZoneInfo

def datetime_indo(dt_obj):
	if not dt_obj:
		return None
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