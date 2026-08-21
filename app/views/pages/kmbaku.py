import flet as ft

def kmbaku_view(page: ft.Page):
	halaman = ft.Text("Halaman KM Baku")

	main_layout = ft.Stack(
		controls=[
			ft.Column(
				halaman
			)
		],
		expand = True
	)

	return ft.Container(
		content=main_layout,
		expand = True
	)