[app]

# (str) Title of your application
title = SteamGrid Overlay

# (str) Package name
package.name = steamgridoverlay

# (str) Package domain (needed for android/ios packaging)
package.domain = com.steamgrid

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements  
# Using specific Pillow version that builds correctly
requirements = python3,kivy,pillow==9.5.0,requests

# (str) Supported orientation (landscape for Ayn Odin Thor!)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API (Android 13 = API 33)
android.api = 33

# (int) Minimum API your APK will support (Android 5.0)
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) python-for-android fork to use (master is unstable, use stable release)
p4a.branch = master

# (str) python-for-android specific commit to use (stable with NDK 25b)
# Leave empty to use latest
# p4a.commit = HEAD

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = False

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for (ARM64 for Snapdragon 8+ Gen 1)
android.archs = arm64-v8a

# (str) python-for-android branch to use
# p4a.branch = master

# (str) python-for-android git clone directory
# p4a.source_dir = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
