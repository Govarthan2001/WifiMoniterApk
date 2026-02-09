
import flet as ft
try:
    print(dir(ft.Icons))
except AttributeError:
    print("ft.Icons not found")
try:
    print(dir(ft.icons))
except AttributeError:
    print("ft.icons not found")
