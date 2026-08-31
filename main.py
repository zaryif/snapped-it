import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

def main():
    # Create QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when toolbar hidden
    app.setApplicationName('Snapped It!')
    app.setOrganizationName('SnappedIt')
    
    # Determine project root (directory containing main.py)
    project_root = str(Path(__file__).parent.resolve())
    
    # Initialize managers
    from app.settings import SettingsManager, SettingsDialog
    from app.screenshot import ScreenshotManager
    from app.recorder import RecordingManager
    from app.hotkeys import HotkeyManager
    from app.toolbar import FloatingToolbar
    from app.tray import SystemTrayManager
    from app.notifications import ToastNotification
    from app.utils import set_window_excluded_from_capture, open_in_file_manager
    
    settings = SettingsManager(project_root)
    screenshot_mgr = ScreenshotManager(settings)
    recording_mgr = RecordingManager(settings)
    hotkey_mgr = HotkeyManager(settings)
    
    # Create UI
    toolbar = FloatingToolbar(settings)
    tray = SystemTrayManager()
    toast = ToastNotification(settings)
    
    # --- Connect Toolbar signals ---
    toolbar.screenshot_requested.connect(
        lambda: screenshot_mgr.capture_fullscreen(toolbar)
    )
    toolbar.screenshot_region_requested.connect(
        lambda: screenshot_mgr.capture_region(toolbar)
    )
    toolbar.recording_toggle_requested.connect(
        lambda: _toggle_recording(recording_mgr, toolbar)
    )
    toolbar.settings_requested.connect(
        lambda: _show_settings(settings, toolbar)
    )
    toolbar.open_folder_requested.connect(
        lambda: _open_folder(settings, project_root)
    )
    
    # --- Connect Tray signals ---
    def _toggle_toolbar():
        if toolbar.isVisible():
            toolbar.hide()
        else:
            toolbar.show()
            toolbar.raise_()
            toolbar.activateWindow()

    tray.show_requested.connect(_toggle_toolbar)
    tray.screenshot_requested.connect(
        lambda: screenshot_mgr.capture_fullscreen(toolbar)
    )
    tray.record_requested.connect(
        lambda: _toggle_recording(recording_mgr, toolbar)
    )
    tray.settings_requested.connect(
        lambda: _show_settings(settings, toolbar)
    )
    tray.open_folder_requested.connect(
        lambda: _open_folder(settings, project_root)
    )
    tray.quit_requested.connect(lambda: _quit(app, hotkey_mgr, recording_mgr, toolbar))
    
    # --- Connect Screenshot signals ---
    screenshot_mgr.screenshot_taken.connect(
        lambda fp: toast.show_notification(fp, 'screenshot') if settings.show_notifications else None
    )
    screenshot_mgr.screenshot_error.connect(
        lambda err: tray.show_message('Screenshot Error', err)
    )
    
    # --- Connect Recording signals ---
    recording_mgr.recording_started.connect(
        lambda: _on_recording_started(toolbar, tray, settings)
    )
    recording_mgr.recording_stopped.connect(
        lambda fp: _on_recording_stopped(toolbar, tray, toast, fp, settings)
    )
    recording_mgr.recording_error.connect(
        lambda err: _on_recording_error(toolbar, tray, err)
    )
    
    # --- Connect Hotkey signals ---
    hotkey_mgr.screenshot_triggered.connect(
        lambda: screenshot_mgr.capture_fullscreen(toolbar)
    )
    hotkey_mgr.recording_triggered.connect(
        lambda: _toggle_recording(recording_mgr, toolbar)
    )
    
    # --- Connect Toast click ---
    toast.clicked.connect(lambda fp: open_in_file_manager(fp))
    
    # --- Connect settings changes ---
    def _apply_settings_changes():
        toolbar.setWindowOpacity(settings.toolbar_opacity)
        exclude = settings.exclude_toolbar_from_capture
        set_window_excluded_from_capture(toolbar, exclude)
    settings.settings_changed.connect(_apply_settings_changes)

    # --- Apply initial window settings after show ---
    _apply_settings_changes()
    
    # Start services
    hotkey_mgr.start()
    
    toolbar.show()
    toolbar.raise_()
    toolbar.activateWindow()
    
    sys.exit(app.exec())

def _toggle_recording(recording_mgr, toolbar):
    if recording_mgr.is_recording:
        recording_mgr.stop_recording()
    else:
        recording_mgr.start_recording(toolbar)

def _on_recording_started(toolbar, tray, settings):
    toolbar.set_recording_state(True)
    tray.set_recording_state(True)
    if settings.exclude_toolbar_from_capture:
        toolbar.hide()

def _on_recording_stopped(toolbar, tray, toast, filepath, settings):
    toolbar.set_recording_state(False)
    tray.set_recording_state(False)
    toolbar.show()
    toolbar.raise_()
    toolbar.activateWindow()
    if settings.show_notifications:
        toast.show_notification(filepath, 'recording')

def _on_recording_error(toolbar, tray, error_msg):
    toolbar.set_recording_state(False)
    tray.set_recording_state(False)
    toolbar.show()
    toolbar.raise_()
    toolbar.activateWindow()
    tray.show_message('Recording Error', error_msg)

def _show_settings(settings, parent):
    from app.settings import SettingsDialog
    dialog = SettingsDialog(settings, parent)
    dialog.exec()

def _open_folder(settings, project_root):
    from app.utils import open_in_file_manager
    save_dir = settings.save_directory
    if save_dir == '.':
        save_dir = project_root
    folder = os.path.join(save_dir, 'Snapped It!')
    os.makedirs(folder, exist_ok=True)
    open_in_file_manager(folder)

def _quit(app, hotkey_mgr, recording_mgr, toolbar):
    if recording_mgr.is_recording:
        recording_mgr.stop_recording()
    hotkey_mgr.stop()
    toolbar.save_geometry_to_settings()
    app.quit()

if __name__ == '__main__':
    main()
