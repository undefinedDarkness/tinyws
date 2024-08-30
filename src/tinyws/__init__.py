import gi
import collections.abc
from .utils.logger import warn, error, info, exception
from json import loads as json_loads
from asyncio import Future

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")

from gi.repository import Gtk, WebKit2, Gio, GLib, Gdk, JavaScriptCore  # type: ignore # noqa: E402

def jsv_to_primitive(v: JavaScriptCore.Value):
    if v.is_undefined() or v.is_null():
        return None
    if v.is_function():
        return lambda *args: jsv_to_primitive(v.function_call(*(JavaScriptCore.Value.new_from_json(arg) for arg in args)))
    else:
        return json_loads(v.to_json(0))
    
def NOP(*args):
    pass

class Webview:
    window: Gtk.Window
    webview: WebKit2.WebView
    webctx: WebKit2.WebContext
    webucm: WebKit2.UserContentManager
    webcfg: WebKit2.Settings

    LOAD_FINISHED = 3

    _store_session: str = ""
    _evaluate_list = {}
    _onload_listeners = []
    _eval_cnt = 0
    _capabilities = []
    _js_code_map = {}  # New attribute to store JavaScript code with eval ID

    def __on_evaluate_result__(self, value):
        eval_id = value.object_get_property_at_index(0).to_int32()
        js_code = self._js_code_map.get(eval_id, "Unknown JavaScript Code")
        result = jsv_to_primitive(value.object_get_property_at_index(1))
        
        if eval_id in self._evaluate_list:
            self._evaluate_list[eval_id](result)
            del self._evaluate_list[eval_id]
        else:
            error(f"Evaluation ID {eval_id} not found in _evaluate_list.")

    def __on_evaluate__(self, obj, result, _):
        try:
            value = self.webview.evaluate_javascript_finish(result)
        except Exception as err:
            error(f"Error during JavaScript evaluation: {err}")
            # Fetch and log the JS code for debugging
            js_code = self._js_code_map.get(self._eval_cnt - 1, "Unknown JavaScript Code")
            error(f"JavaScript code that failed: {js_code}")
            return
        self.__on_evaluate_result__(value)

    def __on_run_javascript__(self, obj, result, _):
        try:
            js_value = self.webview.run_javascript_finish(result)
            if js_value:
                value = js_value.get_js_value()
                self.__on_evaluate_result__(value)
        except Exception as err:
            exception(f"Error during JavaScript run: {err}")
            # Fetch and log the JS code for debugging
            js_code = self._js_code_map.get(self._eval_cnt - 1, "Unknown JavaScript Code")
            exception(f"JavaScript code that failed: {js_code}")
            return

    def apply_stylesheet(self, css=""):
        if css == "":
            warn("apply_stylesheet() called with no source code")
            return
        self.webucm.add_style_sheet(WebKit2.UserStyleSheet(css, 0, 0, None, None))

    def __evaluate__(self, js, cb=True):
        if "evaluate_javascript" in self.webview:
            self.webview.evaluate_javascript(
                js, len(js), None, None, None, self.__on_evaluate__ if cb else NOP, None
            )
        else:
            self.webview.run_javascript(js, None, self.__on_run_javascript__ if cb else NOP, None)

    def evaluate(self, js="", ondone=NOP):
        # info(f"Evaluating {js}")
        result = Future()

        def onCompletion(v):
            ondone(v)
            result.set_result(v)

        if js == "":
            warn("evaluate() called with no source code")
            return
        eval_id = self._eval_cnt
        # Store the JavaScript code with the eval ID
        self._js_code_map[eval_id] = js
        js = f"[{eval_id}, ({js})]"
        self._evaluate_list[eval_id] = onCompletion
        self.__evaluate__(js)
        self._eval_cnt += 1
        return result

    def onload(self, fn, noOfTimes=float("inf")):
        self._onload_listeners.append([fn, noOfTimes])

    def _onload(self, _, evt):
        if evt == self.LOAD_FINISHED:
            for idx in range(0, len(self._onload_listeners)):
                if self._onload_listeners[idx][1] > 0:
                    self._onload_listeners[idx][0]()
                self._onload_listeners[idx][1] -= 1

    def register_handler(self, name, onmessage=NOP):
        self.webucm.register_script_message_handler(name)
        self.webucm.connect(
            f"script-message-received::{name}",
            lambda _, x: onmessage(jsv_to_primitive(x.get_js_value())),
        )

    def _welcome_msg(self):
        print("✨ \u001b[1mTINYWS\u001b[0m ✨")
        info(
            f"Using Gtk Version {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}"
        )
        info(
            f"Using Webkit2Gtk Version {WebKit2.get_major_version()}.{WebKit2.get_minor_version()}.{WebKit2.get_micro_version()}"
        )

        if "evaluate_javascript" not in self.webview:
            warn("OLD WEBKIT2GTK VERSION")

    def __init__(
        self,
        inspect=False,
        transparent=False,
        html=None,
        forward_console=True,
        window_css="",
        persistent=None,
        decorated=True,
        exit_on_window_close=True,
        title="Webview",
        visible=True,
        url=None,
        window_type=Gdk.WindowTypeHint.DIALOG,
        position=Gtk.WindowPosition.CENTER,
        x=-1,
        y=-1,
        width="800",
        height="600",
        ephemeral=True,
        capabilities=[]
    ):
        if isinstance(width, str) and width.endswith("%"):
            width = width.strip()
            width = int(float(width[:-1]) / 100 * Gdk.Screen.width())
        else:
            width = int(width)
        if isinstance(height, str) and height.endswith("%"):
            height = height.strip()
            height = int(float(height[:-1]) / 100 * Gdk.Screen.height())
        else:
            height = int(height)

        if x >= 0 and y >= 0:
            self.onload(lambda: self.window.move(x, y), 1)

        self.window = Gtk.Window(
            title=title, type_hint=window_type, decorated=decorated
        )
        self.window.set_position(position)
        self.window.set_default_size(width, height)
        self.webctx = WebKit2.WebContext.new() if not ephemeral else WebKit2.WebContext.new_ephemeral() 
        self.webview = WebKit2.WebView.new_with_context(self.webctx)

        self._welcome_msg()
        info(f"Creating window of size ({width}, {height})")

        if transparent:
            self.window.set_visual(self.window.get_screen().get_rgba_visual())
            self.webview.set_background_color(
                Gdk.RGBA(0, 0, 0, 0)
            )  # Set webview background transparent
            window_css += "window { background-color: rgba(0,0,0,0); }"

        if window_css:
            style_provider = Gtk.CssProvider()
            style_provider.load_from_data(bytes(window_css, "utf-8"))
            Gtk.StyleContext.add_provider_for_screen(
                self.window.get_screen(),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

        self.webcfg = self.webview.get_settings()
        self.webcfg.set_enable_write_console_messages_to_stdout(forward_console)
        self.webcfg.set_allow_universal_access_from_file_urls(True)
        self.webcfg.set_allow_file_access_from_file_urls(True)
        self.webcfg.set_enable_developer_extras(True)
        self.webview.set_settings(self.webcfg)

        if url:
            self.webview.load_uri(url)

        if html:
            self.webview.load_html(html, "file://")

        self.webucm = self.webview.get_user_content_manager()

        if inspect:
            inspector = self.webview.get_inspector()
            inspector.show()

        if persistent:
            info("Storing session data & cookies")
            self._store_session = persistent[0]
            cookie_manager = self.webctx.get_cookie_manager()
            cookie_manager.set_persistent_storage(
                persistent[1], WebKit2.CookiePersistentStorage.TEXT
            )

        self.onload(lambda: self.evaluate("console.log(`[tinyws] Ready!`)"), 1)
        self._capabilities = capabilities
        self.onload(self.registerCapabilities)

        self.window.add(self.webview)

        if exit_on_window_close:
            self.window.connect("destroy", lambda _: self.__cleanup__())

        self.webview.connect("load-changed", self._onload)

        if visible:
            self.window.show_all()

    def registerCapabilities(self):
        self.evaluate("(() => { window.capabilities = {} })()")
        for cap in self._capabilities:
            cap.__register__(self)

    def __enter__(self):
        return self

    def __cleanup__(self):
        if self._store_session != "":
            session_state = self.webview.get_session_state()
            session_state_data = session_state.serialize().get_data()

            with open(self._store_session, "wb") as f:
                f.write(session_state_data)

        Gtk.main_quit()

    def run(self):
        Gtk.main()
