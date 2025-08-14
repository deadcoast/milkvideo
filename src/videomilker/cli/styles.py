"""Rich styles and themes for VideoMilker CLI."""

from rich.style import Style
from rich.theme import Theme


# Custom styles
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)
PROGRESS_STYLE = Style(color="cyan", bold=True)

# Menu styles
MENU_TITLE_STYLE = Style(color="blue", bold=True)
MENU_OPTION_STYLE = Style(color="white")
MENU_SELECTED_STYLE = Style(color="cyan", bold=True)

# Download styles
DOWNLOAD_PROGRESS_STYLE = Style(color="green")
DOWNLOAD_ERROR_STYLE = Style(color="red")
DOWNLOAD_SUCCESS_STYLE = Style(color="green", bold=True)

# Custom theme
VIDEOMILKER_THEME = Theme(
    {
        "success": SUCCESS_STYLE,
        "error": ERROR_STYLE,
        "warning": WARNING_STYLE,
        "info": INFO_STYLE,
        "progress": PROGRESS_STYLE,
        "menu.title": MENU_TITLE_STYLE,
        "menu.option": MENU_OPTION_STYLE,
        "menu.selected": MENU_SELECTED_STYLE,
        "download.progress": DOWNLOAD_PROGRESS_STYLE,
        "download.error": DOWNLOAD_ERROR_STYLE,
        "download.success": DOWNLOAD_SUCCESS_STYLE,
    }
)
