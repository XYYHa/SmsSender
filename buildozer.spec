[app]

# 包名
package.name = SmsSender

# 包域名（唯一标识）
package.domain = com.smssender.app

# 源码目录
source.dir = .

# 入口文件
source.main = main.py

# 额外的Python源码文件会包含进来
source.include_exts = py,png,jpg,kv,atlas

# 版本
version = 1.0.0

# 需求：Kivy做UI（加上iOS玻璃效果），pycryptodome包含Crypto模块
requirements = python3, kivy, requests, pycryptodome, urllib3, pillow

# Android最低API版本
android.min_api = 21

# Android目标API版本
android.api = 34

# Android NDK版本（r25c稳定兼容）
android.ndk = 25c

# Android SDK版本
android.sdk = 34

# 权限
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, POST_NOTIFICATIONS

# 权限（Kivy需要前台Activity显示UI）
android.manifest = <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    
    <application android:label="短信发送器" android:allowBackup="true"
                 android:theme="@android:style/Theme.Material.NoActionBar">
    </application>

# 支持的架构
android.archs = arm64-v8a

# 日志级别
android.log_level = 2

# 是否使用Python的配方缓存
android.copy_libs = True

# 是否启用AndroidX
android.enable_androidx = True

# 启用全屏（iOS风格无边栏）
android.fullscreen = 1

# 生成Presplash（启动图保持深色毛玻璃风格）
android.enable_presplash = 1
android.presplash_color = #1C1C1E

# 隐藏状态栏
android.window_soft_input_mode = adjustResize

# 去广告/统计相关
android.gradle_dependencies = ''

[buildozer]

# 日志级别
log_level = 2

# 构建时警告
warn_on_root = 0