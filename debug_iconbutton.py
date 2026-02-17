import flet as ft
import sys

print(f"Python: {sys.version}")
print(f"Flet version: {ft.version}")

try:
    print("Attempt 1: icon string")
    b1 = ft.IconButton(icon="play_arrow")
    print("Success 1")
except Exception as e:
    print(f"Fail 1: {e}")

try:
    print("Attempt 2: icon control passed to icon arg")
    b2 = ft.IconButton(icon=ft.Icon("play_arrow"))
    print("Success 2")
except Exception as e:
    print(f"Fail 2: {e}")

try:
    print("Attempt 3: content arg")
    b3 = ft.IconButton(content=ft.Icon("play_arrow"))
    print("Success 3")
except Exception as e:
    print(f"Fail 3: {e}")

try:
    print("Attempt 4: icon string with color")
    b4 = ft.IconButton(icon="play_arrow", icon_color="blue")
    print("Success 4")
except Exception as e:
    print(f"Fail 4: {e}")

try:
    print("Attempt 5: explicit None content")
    b5 = ft.IconButton(icon="play_arrow", content=None)
    print("Success 5")
except Exception as e:
    print(f"Fail 5: {e}")
