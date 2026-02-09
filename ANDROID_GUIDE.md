# Converting to Android APK

## ⚠️ Important Limitations
Converting this specific Wifi application to an Android APK is not straightforward for two main reasons:

1. **Library Incompatibility**: 
   - The current code uses `pywifi`, which relies on Windows/Linux system calls.
   - **Android does not support `pywifi`**.
   - To scan Wifi on Android, an app must use Android's Native APIs (Java/Kotlin) and requires specific permissions (`ACCESS_FINE_LOCATION`, `NEARBY_WIFI_DEVICES`).
   - Python apps on Android (via Flet or Kivy) must use a bridge (like `pyjnius`) to talk to these Java APIs.

2. **Missing Build Tools**:
   - Building an APK requires the **Flutter SDK** and **Android SDK** (Android Studio) to be installed on your machine.
   - Your system currently does not have `flutter` installed.

## Recommended Path for Android

If you strictly need this to run on Android, the approach depends on how comfortable you are with setting up development environments.

### Option A: Use Kivy + Buildozer (Standard for Python Android Apps)
Kivy is the most mature framework for accessing Android hardware from Python.

1. **Rewrite the App**: Port the UI from Flet to **Kivy**.
2. **Native Access**: Use `from jnius import autoclass` to access Android's `WifiManager`.
3. **Build**: Use **Buildozer** (requires Linux or WSL on Windows) to compile the APK.

### Option B: Flet + Flutter Build
If you want to stick with Flet:

1. **Install Prerequisites**:
   - [Install Flutter SDK](https://docs.flutter.dev/get-started/install/windows)
   - [Install Android Studio](https://developer.android.com/studio) (for Android SDK & command line tools)
2. **Fix Code**: 
   - You cannot use `pywifi`. 
   - You would likely need to write a **custom Flet control in Dart** (Flutter) to handle Wifi scanning, or find a Python package that abstracts this for Flet (very rare currently).
3. **Build Command**:
   ```bash
   flet build apk
   ```

## Conclusion
Because `pywifi` essentially only works on Desktop, simply "building" the current code for mobile will result in an app that opens but **crashes** or does nothing when you click "Scan".

For a mobile Wifi scanner, we strongly recommend using a native development tool (Kotlin/Swift) or a cross-platform tool with mature native plugin support (React Native/Flutter), rather than Python, due to the strict OS permissions required for Wifi scanning.
