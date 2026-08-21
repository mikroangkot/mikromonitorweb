import flet as ft

def history_view(page: ft.Page):
	halaman = ft.Text("Halaman History")

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