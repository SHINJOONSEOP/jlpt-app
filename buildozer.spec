[app]
title = JLPT 단어학습
package.name = jlptapp
package.domain = org.jlpt

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt,csv
source.include_patterns = *.ttf,*.json,*.csv

version = 1.0

requirements = python3,kivy==2.1.0,requests

orientation = portrait
fullscreen = 0

android.minapi = 26
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,VIBRATE

android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
