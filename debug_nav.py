import flet as ft

try:
    print("Attempt 1: NavRailDest with icon string")
    d1 = ft.NavigationRailDestination(icon="terminal", label="Terminal")
    print("Success 1")
except Exception as e:
    print(f"Fail 1: {e}")

try:
    print("Attempt 2: NavRailDest with icon_content")
    d2 = ft.NavigationRailDestination(icon_content=ft.Icon("terminal"), label="Terminal")
    print("Success 2")
except Exception as e:
    print(f"Fail 2: {e}")
