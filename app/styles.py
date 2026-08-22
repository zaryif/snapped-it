"""Dark theme color palette and QSS stylesheets for Snapped It! (Dynamic Island edition)."""

class Colors:
    """Application color palette — pitch black minimal theme."""
    BG_DARK = "#000000"
    BG_SURFACE = "#111111"
    BG_SURFACE_HOVER = "#222222"
    ACCENT_BLUE = "#007aff"
    ACCENT_RED = "#ff3b30"
    ACCENT_RED_HOVER = "#ff453a"
    ACCENT_RED_PRESSED = "#d72c21"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8e8e93"
    TEXT_MUTED = "#3a3a3c"
    BORDER = "#1c1c1e"
    SHADOW = "rgba(0, 0, 0, 0.6)"
    SUCCESS = "#34c759"

def get_screenshot_button_stylesheet() -> str:
    """QSS for the minimalist white screenshot button."""
    return f"""
        QPushButton#screenshot_btn {{
            background-color: #ffffff;
            color: #000000;
            border: none;
            border-radius: 12px;
            min-width: 24px;
            min-height: 24px;
            max-width: 24px;
            max-height: 24px;
        }}
        QPushButton#screenshot_btn:hover {{
            background-color: #e5e5ea;
        }}
        QPushButton#screenshot_btn:pressed {{
            background-color: #d1d1d6;
        }}
    """

def get_record_button_stylesheet(is_recording: bool = False) -> str:
    """QSS for the minimalist red record button."""
    if is_recording:
        return f"""
            QPushButton#record_btn {{
                background-color: {Colors.ACCENT_RED};
                border: none;
                border-radius: 4px;
                min-width: 20px;
                min-height: 20px;
                max-width: 20px;
                max-height: 20px;
            }}
            QPushButton#record_btn:hover {{
                background-color: {Colors.ACCENT_RED_HOVER};
            }}
            QPushButton#record_btn:pressed {{
                background-color: {Colors.ACCENT_RED_PRESSED};
            }}
        """
    else:
        return f"""
            QPushButton#record_btn {{
                background-color: {Colors.ACCENT_RED};
                border: none;
                border-radius: 12px;
                min-width: 24px;
                min-height: 24px;
                max-width: 24px;
                max-height: 24px;
            }}
            QPushButton#record_btn:hover {{
                background-color: {Colors.ACCENT_RED_HOVER};
            }}
            QPushButton#record_btn:pressed {{
                background-color: {Colors.ACCENT_RED_PRESSED};
            }}
        """

def get_timer_label_stylesheet() -> str:
    """QSS for the recording timer label."""
    return f"""
        QLabel#timer_label {{
            color: {Colors.TEXT_PRIMARY};
            background: transparent;
            font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
            font-size: 13px;
            font-weight: bold;
        }}
    """

def get_slider_stylesheet() -> str:
    """QSS for the opacity slider."""
    return f"""
        QSlider::groove:horizontal {{
            background: #2c2c2e;
            height: 4px;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: #ffffff;
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: #e5e5ea;
        }}
        QSlider::sub-page:horizontal {{
            background: #ffffff;
            border-radius: 2px;
        }}
    """

def get_toast_stylesheet() -> str:
    """QSS for toast notification popup."""
    return f"""
        QWidget#toast {{
            background-color: rgba(10, 10, 10, 240);
            border: 1px solid #1c1c1e;
            border-radius: 14px;
        }}
        QLabel#toast_title {{
            color: #ffffff;
            font-size: 13px;
            font-weight: bold;
        }}
        QLabel#toast_path {{
            color: #8e8e93;
            font-size: 11px;
        }}
        QLabel#toast_thumb {{
            border: 1px solid #2c2c2e;
            border-radius: 6px;
            background-color: #111111;
        }}
    """

def get_settings_dialog_stylesheet() -> str:
    """QSS for the settings dialog — ultra minimalist flat style."""
    return f"""
        QDialog {{
            background-color: #000000;
            color: #ffffff;
        }}
        QLabel {{
            color: #ffffff;
            font-size: 13px;
        }}
        QLabel#section_label {{
            color: #8e8e93;
            font-size: 11px;
        }}
        QCheckBox {{
            color: #ffffff;
            font-size: 13px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid #2c2c2e;
            border-radius: 4px;
            background: #111111;
        }}
        QCheckBox::indicator:checked {{
            background-color: #ffffff;
            border-color: #ffffff;
        }}
        QComboBox {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #2c2c2e;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            min-width: 120px;
        }}
        QComboBox:hover {{
            border-color: #3a3a3c;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #2c2c2e;
            selection-background-color: #222222;
        }}
        QLineEdit {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #2c2c2e;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: #ffffff;
        }}
        QPushButton {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #2c2c2e;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #222222;
            border-color: #3a3a3c;
        }}
        QPushButton#save_btn {{
            background-color: #ffffff;
            color: #000000;
            border: none;
        }}
        QPushButton#save_btn:hover {{
            background-color: #e5e5ea;
        }}
        QGroupBox {{
            color: #ffffff;
            border: none;
            border-top: 1px solid #1c1c1e;
            margin-top: 16px;
            padding-top: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 0px;
            padding: 0 4px;
            color: #8e8e93;
        }}
        QTabWidget::pane {{
            background-color: #000000;
            border: 1px solid #1c1c1e;
            border-radius: 0 0 8px 8px;
        }}
        QTabBar::tab {{
            background-color: #111111;
            color: #8e8e93;
            border: 1px solid #1c1c1e;
            padding: 8px 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        QTabBar::tab:selected {{
            background-color: #000000;
            color: #ffffff;
            border-bottom: 2px solid #ffffff;
        }}
        QTabBar::tab:hover {{
            color: #ffffff;
        }}
        QSpinBox {{
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #2c2c2e;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 13px;
        }}
    """

def get_region_overlay_stylesheet() -> str:
    """QSS for the region selector overlay."""
    return f"""
        QWidget#region_overlay {{
            background-color: rgba(0, 0, 0, 0);
        }}
        QLabel#dimension_label {{
            color: #ffffff;
            background-color: rgba(0, 0, 0, 200);
            border: 1px solid #2c2c2e;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
            font-size: 11px;
        }}
    """
