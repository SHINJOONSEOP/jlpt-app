[app]
# 앱 기본 정보
title = JLPT 단어학습
package.name = jlptapp
package.domain = org.jlpt

# 소스 설정
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt,csv

# 폰트 파일 포함
source.include_patterns = *.ttf,*.json,*.csv

# 앱 버전
version = 1.0

# 필수 패키지
requirements = python3,kivy==2.3.0,requests

# 앱 방향 (세로 고정)
orientation = portrait

# 화면 설정
fullscreen = 0

# Android 설정
android.minapi = 26
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# 권한
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,VIBRATE

# 빌드 설정
android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
