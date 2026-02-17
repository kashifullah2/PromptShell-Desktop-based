import flet as ft
import inspect

print(f"Flet version: {ft.version}")

try:
    print("IconButton signature:", inspect.signature(ft.IconButton.__init__))
except Exception as e:
    print(f"Could not get signature: {e}")

try:
    print("Has content param:", 'content' in inspect.signature(ft.IconButton.__init__).parameters)
except:
    pass

try:
    # Try to find play arrow in icons
    import flet.icons as icons
    print("Checking icons module...")
    if hasattr(icons, 'PLAY_ARROW'):
        print("Found PLAY_ARROW in icons.")
    else:
        print("PLAY_ARROW NOT found in icons.")
        # Print a few available icons
        print("Available icons sample:", [x for x in dir(icons) if not x.startswith('_')][:10])
except ImportError:
    print("Could not import flet.icons")

try:
    btn = ft.IconButton(icon="play_arrow")
    print("IconButton(icon='play_arrow') instantiated successfully.")
except Exception as e:
    print(f"IconButton(icon='play_arrow') failed: {e}")
