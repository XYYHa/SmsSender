[app]

title = SmsSender

package.name = SmsSender

package.domain = com.smssender.app

source.dir = .

source.main = main.py

source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3, kivy, requests, pycryptodome, urllib3, pillow

android.min_api = 21

android.api = 34

android.ndk = 25c

android.sdk = 34

android.accept_sdk_license = True

android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, POST_NOTIFICATIONS

android.manifest = <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    
    <application android:label="短信发送器" android:allowBackup="true"
                 android:theme="@Android:style/Theme.Material.NoActionBar">
    </application>

android.archs = arm64-v8a

android.log_level = 2

android.copy_libs = True

android.enable_androidx = True

android.fullscreen = 1

android.enable_presplash = 1
android.presplash_color = #1C1C1E

android.window_soft_input_mode = adjustResize

# android.gradle_dependencies = 

[buildozer]
log_level = 2
warn_on_root = 0