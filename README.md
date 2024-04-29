# Tiny Widget System
This is a tiny 1 file widget system that works by being just a thin layer between Webkit2Gtk and your system,
Allowing you to easily script webpages to behave as your widgets,

# API

## Parameters (Passed to constructor)
- inspect - Show the webpage inspector on startup (Recommended for debug)
- transparent - Make the window transparent
- html - HTML document as a string
- forward_console - Write DOM console.log() messages to STDOUT (Recommended for debug) 
- window_css - GTK CSS to apply to the window
- decorated - Decorate (Add titlebar) to GTK Window
- exit_on_window_close - "
- title - "
- visible - "
- url - Can be used instead of `html`
- window_type - [Gdk Window Type Hint](https://docs.gtk.org/gdk3/enum.WindowTypeHint.html)


To tweak these after `webview.run()`, please refer to source code and modify 

## API
