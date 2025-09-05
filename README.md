# DualSense Swipe Project

This repo is ready to build into a Windows .exe using GitHub Actions.

## 🚀 How to Build Your EXE

1. Create a GitHub account at [github.com](https://github.com).
2. Create a new repository (public or private).
3. Upload all the files from this project (including the `.github` folder).
4. Go to the "Actions" tab in your repo and enable workflows.
5. Run the "Build DualSense EXE" workflow manually (or push code to `main`).
6. After it completes, download the artifact named **DualSense-EXE** — it contains your `dualsense_swipe.exe`.

## ℹ️ Notes
- The build runs on `windows-latest` with PyInstaller, so all required DLLs are collected automatically.
- DualSense drivers must still be installed on the target machine for the controller to work properly.
