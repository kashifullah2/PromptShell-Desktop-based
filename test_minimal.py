import flet as ft

def main(page: ft.Page):
    page.title = "Minimal Test"
    page.add(ft.Text("Hello World"))
    print("Minimal app loaded")

if __name__ == "__main__":
    ft.app(target=main)
