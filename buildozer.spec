[app]
title = 加班薪资记录仪
package.name = overtimerecorder
package.domain = org.myapp
source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas
version = 1.2.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
