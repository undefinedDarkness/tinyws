import argparse
from src.tinyws import Webview, Gtk, Gdk  # Assuming the provided code is in a file named webview.py
# from gi.repository import Gdk, Gtk

def main():
    parser = argparse.ArgumentParser(description="Create a webview with custom settings")
    parser.add_argument("--url", default="https://google.com", help="URL to load in the webview")
    parser.add_argument("--html", help="HTML content to load in the webview")
    parser.add_argument("--title", default="Webview", help="Window title")
    parser.add_argument("--width", default="800", help="Window width")
    parser.add_argument("--x", default=-1, type=int, help="Window position x")
    parser.add_argument("--y", default=-1, type=int, help="Window position y")
    parser.add_argument("--height", default="600", help="Window height")
    parser.add_argument("--inspect", action="store_true", help="Enable inspector")
    parser.add_argument("--transparent", action="store_true", help="Enable transparent background")
    parser.add_argument("--decorated", action="store_true", help="Disable window decoration")
    parser.add_argument("--persistent", nargs=2, metavar=('SESSION_FILE', 'COOKIE_FILE'), help="Enable persistent storage")
    parser.add_argument("--css", help="Custom CSS for the window")
    parser.add_argument("--window-type", default="DIALOG", choices=["NORMAL", "DIALOG", "DOCK", "DESKTOP", "POPUP", "TOOLBAR", "MENU", "UTILITY", "SPLASHSCREEN", "DROPDOWN_MENU", "TOOLTIP"], help="Window type")
    parser.add_argument("--window-position", default="CENTER", choices=["CENTER", "MOUSE", "CENTER_ALWAYS", "CENTER_ON_PARENT"], help="Window position")

    args = parser.parse_args()

    window_type = getattr(Gdk.WindowTypeHint, args.window_type)
    window_position = getattr(Gtk.WindowPosition, args.window_position)

    webview = Webview(
        inspect=args.inspect,
        transparent=args.transparent,
        html=args.html,
        decorated=args.decorated,
        title=args.title,
        url=args.url,
        x=args.x,
        y=args.y,
        width=args.width,
        height=args.height,
        persistent=args.persistent,
        window_css=args.css or "",
        window_type=window_type,
        position=window_position
    )

    webview.run()

if __name__ == "__main__":
    main()