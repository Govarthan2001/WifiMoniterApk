# Wifi Monitor App

This is a Python application built with [Flet](https://flet.dev) that monitors your Wifi connection and lists available networks.

## Features
- **Scan Networks**: Lists available Wifi networks and their signal strength.
- **Connection Monitor**: Continuously checks which network you are connected to.
- **Auto-Redirect**: If connected to a specified "Target Wifi" (configurable in the app), it automatically opens `welcome.html`.

## Prerequisites
- Windows (Recommended for `pywifi` usage)
- Python 3.x
- A Wifi Adapter

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App
Run the main script:
```bash
python main.py
```

## Note on Mobile (Android/iOS)
This application uses `pywifi` which is primarily for Desktop (Windows/Linux) environments. 
To build a true mobile app that scans Wifi on Android/iOS, you would typically use **Kivy** with **Buildozer** and access Android APIs via `pyjnius`, as strict permissions prevent standard Python libraries from scanning Wifi on mobile devices.

However, Flet (used here) is great for responsive UI and can be packaged for mobile, but the backend Wifi scanning logic would need platform-specific adjustments for Android.
