
import flet as ft
import time
import threading
import os
import platform

# Attempt to import pywifi, set flag if successful
try:
    import pywifi
    from pywifi import const
    PYWIFI_AVAILABLE = True
except ImportError:
    PYWIFI_AVAILABLE = False

class WifiApp:
    def __init__(self):
        self.wifi = None
        self.iface = None
        self.target_ssid = "TargetWiFi" # Default
        self.current_ssid = None
        self.scanning = False
        self.networks = []
        
        if PYWIFI_AVAILABLE:
            try:
                self.wifi = pywifi.PyWiFi()
                self.iface = self.get_interface()
            except Exception as e:
                print(f"Wifi init error: {e}")

    def get_interface(self):
        if not self.wifi: return None
        try:
            interfaces = self.wifi.interfaces()
            if interfaces:
                return interfaces[0]
        except Exception:
            return None
        return None

    def scan_networks(self):
        if not PYWIFI_AVAILABLE or not self.iface:
            # Return dummy data for testing if not available (e.g. on Android without native plugin)
            if platform.system() != "Windows":
                 return [] 
            return []
        
        try:
            self.iface.scan()
            time.sleep(2) # Wait for scan to complete
            results = self.iface.scan_results()
            
            # Deduplicate and sort by signal strength
            unique_networks = {}
            for network in results:
                if network.ssid and network.ssid not in unique_networks:
                    unique_networks[network.ssid] = network
            
            sorted_networks = sorted(unique_networks.values(), key=lambda x: x.signal, reverse=True)
            return sorted_networks
        except Exception as e:
            print(f"Scan error: {e}")
            return []

    def get_connected_ssid(self):
        # Initial check using pywifi if available
        if self.iface:
            try:
                if self.iface.status() == const.IFACE_CONNECTED:
                    pass # Continue to OS check for verified SSID
            except Exception:
                pass
        
        # Windows specific check
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"])
                result = result.decode("utf-8", errors="ignore")
                for line in result.split("\n"):
                    if "SSID" in line and "BSSID" not in line:
                         return line.split(":")[1].strip()
            except Exception:
                pass
        return None

def main(page: ft.Page):
    page.title = "Wifi Manager"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 400
    page.window_height = 800
    
    # Modern Color Palette
    BG_GRADIENT = ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=["#1a1a2e", "#16213e", "#0f3460"]
    )
    CARD_BG = ft.Colors.WHITE_10
    ACCENT_COLOR = "#e94560"
    TEXT_COLOR = ft.Colors.WHITE
    
    wifi_app = WifiApp()
    
    # UI Components
    status_text = ft.Text("Ready to scan", size=14, color=ft.Colors.WHITE_70, italic=True)
    current_network_text = ft.Text("Not Connected", size=24, weight=ft.FontWeight.BOLD, color=ACCENT_COLOR)
    
    network_list = ft.ListView(expand=True, spacing=15, padding=20)
    
    def on_scan_click(e):
        status_text.value = "Scanning..."
        scan_btn.content.controls[1].value = "Scanning..."
        scan_btn.disabled = True
        page.update()
        
        # Run scan in thread
        def scan_task():
            networks = wifi_app.scan_networks()
            
            def update_ui():
                network_list.controls.clear()
                if not networks:
                    network_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.WIFI_OFF, size=50, color=ft.Colors.WHITE_54),
                                ft.Text("No networks found", color=ft.Colors.WHITE_54)
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            alignment=ft.alignment.Alignment(0, 0),
                            padding=20
                        )
                    )
                
                for net in networks:
                    # Use generic wifi icon to avoid AttributeErrors
                    signal_icon = ft.Icons.WIFI
                    # Simple signal strength logic for icon color or opacity if needed
                    signal = getattr(net, 'signal', -100)
                    
                    network_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(signal_icon, color=TEXT_COLOR, size=24),
                                    padding=10,
                                    bgcolor="#334aa3df",
                                    border_radius=50
                                ),
                                ft.Column([
                                    ft.Text(getattr(net, 'ssid', 'Unknown'), weight=ft.FontWeight.BOLD, size=16, color=TEXT_COLOR),
                                    ft.Text(f"Signal: {signal} dBm", size=12, color=ft.Colors.WHITE_60)
                                ], spacing=2)
                            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            bgcolor=ft.Colors.WHITE_12,
                            border_radius=15,
                            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
                            on_hover=lambda e: e.control.update() # Placeholder for hover effect
                        )
                    )
                status_text.value = f"Found {len(networks)} networks"
                scan_btn.content.controls[1].value = "Scan Networks"
                scan_btn.disabled = False
                page.update()
            
            update_ui()
            
        t = threading.Thread(target=scan_task)
        t.start()

    def check_connection_loop():
        browser_opened = False
        while True:
            ssid = wifi_app.get_connected_ssid()
            if ssid:
                current_network_text.value = ssid
                current_network_text.color = "#4ade80" # Greenish
                
                # Check target
                target = target_input.value
                if target and ssid == target:
                    if not browser_opened:
                        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welcome.html")
                        page.launch_url(f"file:///{file_path}")
                        browser_opened = True
                else:
                    browser_opened = False
            else:
                current_network_text.value = "Disconnected"
                current_network_text.color = ACCENT_COLOR
                browser_opened = False
            
            page.update()
            time.sleep(5)

    scan_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WIFI_FIND if hasattr(ft.Icons, "WIFI_FIND") else ft.Icons.SEARCH, color=TEXT_COLOR),
            ft.Text("Scan Networks", size=16, weight=ft.FontWeight.W_600, color=TEXT_COLOR)
        ], alignment=ft.MainAxisAlignment.CENTER),
        on_click=on_scan_click,
        bgcolor="#4ecca3", # Teal-ish
        padding=15,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color="#664ecca3",
            offset=ft.Offset(0, 4),
        ),
        ink=True,
    )

    target_input = ft.TextField(
        label="Target Wifi SSID", 
        value="realme 10 Pro+ 5G",
        hint_text="Enter SSID to auto-open page",
        border_radius=12,
        bgcolor=ft.Colors.WHITE_10,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT_COLOR,
        text_style=ft.TextStyle(color=TEXT_COLOR),
        label_style=ft.TextStyle(color=ft.Colors.WHITE_70)
    )

    # Main Layout
    page.add(
        ft.Container(
            content=ft.Column([
                # Header Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Wifi Monitor", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Connected To:", size=12, color=ft.Colors.WHITE_60, weight=ft.FontWeight.BOLD),
                                current_network_text,
                            ]),
                            padding=20,
                            bgcolor=CARD_BG,
                            border_radius=20,
                            width=float("inf"),
                        ),
                    ]),
                    padding=20
                ),
                
                # Controls Section
                ft.Container(
                    content=ft.Column([
                        target_input,
                        ft.Container(height=10),
                        scan_btn,
                        ft.Container(height=5),
                        ft.Container(content=status_text, alignment=ft.alignment.Alignment(0, 0)),
                    ]),
                    padding=ft.padding.only(left=20, right=20, bottom=10)
                ),
                
                ft.Divider(color=ft.Colors.WHITE_24, thickness=1),
                
                # List Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Available Networks", size=18, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                        ft.Container(
                            content=network_list,
                            expand=True # Let list take remaining space
                        )
                    ]),
                    padding=ft.padding.only(left=20, right=20, top=10),
                    expand=True
                )
            ], spacing=0),
            gradient=BG_GRADIENT,
            expand=True,
        )
    )

    # Start monitor thread
    t = threading.Thread(target=check_connection_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    ft.app(target=main)
