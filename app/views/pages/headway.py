import flet as ft

def headway_view(page: ft.Page):
	halaman = ft.Text("Halaman Headway")

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