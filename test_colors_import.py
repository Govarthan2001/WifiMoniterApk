
import flet as ft
try:
    from flet import colors
    print("Imported colors successfully")
    print(colors.with_opacity(0.5, "red"))
except ImportError:
    print("Could not import colors")

try:
    print(ft.colors.with_opacity(0.5, "red"))
except AttributeError:
    print("ft.colors not found")
