import flet as ft

def unit_view(page: ft.Page):
	halaman = ft.Text("Halaman Unit")

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