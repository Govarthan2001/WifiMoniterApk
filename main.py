
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
    page.padding = 20
    page.window_width = 400
    page.window_height = 700
    
    wifi_app = WifiApp()
    
    # UI Components
    status_text = ft.Text("Ready to scan", size=16, color=ft.Colors.GREY_400)
    current_network_text = ft.Text("Not Connected", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    
    network_list = ft.ListView(expand=True, spacing=10, padding=10)
    
    def on_scan_click(e):
        status_text.value = "Scanning..."
        scan_btn.disabled = True
        page.update()
        
        # Run scan in thread
        def scan_task():
            networks = wifi_app.scan_networks()
            
            def update_ui():
                network_list.controls.clear()
                if not networks:
                    network_list.controls.append(ft.Text("No networks found or scanning not supported."))
                
                for net in networks:
                    # Use generic wifi icon to avoid AttributeErrors
                    signal_icon = ft.Icons.WIFI
                    # Simple signal strength logic for icon color or opacity if needed
                    # checking signal if available
                    signal = getattr(net, 'signal', -100)
                    
                    network_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(signal_icon, color=ft.Colors.WHITE),
                                ft.Column([
                                    ft.Text(getattr(net, 'ssid', 'Unknown'), weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Signal: {signal} dBm", size=12, color=ft.Colors.GREY_500)
                                ])
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                            border_radius=10
                        )
                    )
                status_text.value = f"Found {len(networks)} networks"
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
                current_network_text.color = ft.Colors.GREEN_400
                
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
                current_network_text.color = ft.Colors.RED_400
                browser_opened = False
            
            page.update()
            time.sleep(5)

    scan_btn = ft.ElevatedButton(
        "Scan Networks", 
        icon=ft.Icons.WIFI_FIND if hasattr(ft.Icons, "WIFI_FIND") else ft.Icons.SEARCH, 
        on_click=on_scan_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        height=50
    )

    target_input = ft.TextField(
        label="Target Wifi SSID", 
        value="MyHomeNetwork",
        hint_text="Enter SSID to auto-open page",
        border_radius=10
    )

    page.add(
        ft.Column([
            ft.Text("Wifi Monitor", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Text("Connected To:", size=14, color=ft.Colors.GREY_400),
            current_network_text,
            ft.Container(height=20),
            target_input,
            ft.Container(height=10),
            scan_btn,
            status_text,
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Text("Available Networks:", size=16, weight=ft.FontWeight.BOLD),
            network_list
        ], 
        height=650, # constrain height
        scroll=ft.ScrollMode.HIDDEN
        )
    )

    # Start monitor thread
    t = threading.Thread(target=check_connection_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    ft.app(target=main)
