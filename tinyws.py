import gi
from logging import warn, error 
import collections.abc
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')

from gi.repository import Gtk, WebKit2, Gio, GLib, Gdk, JavaScriptCore

class JSVArray(collections.abc.Sequence):
    arr_v: JavaScriptCore.Value

    def __init__(self, arr_v):
        self.arr_v = arr_v

    def __len__(self) -> int:
        return jsv_to_primitive(self.arr_v.object_get_property("length")) # type: ignore

    def __str__(self):
        l = []
        for i in range(0, len(self)):
            l.insert(i, self[i])
        return str(l)

    def __getitem__(self, idx):
        return jsv_to_primitive(self.arr_v.object_get_property_at_index(idx))

def jsv_to_primitive(v: JavaScriptCore.Value):
    if v.is_boolean():
        return v.to_boolean()
    elif v.is_null() or v.is_undefined():
        warn("Conversion from null or undefined object")
        return None
    elif v.is_number():
        d = v.to_double()
        return d if not d.is_integer() else v.to_int32() 
    elif v.is_string():
        return v.to_string()
    elif v.is_function():
        return lambda *args: jsv_to_primitive(v.function_call(*args))
    elif v.is_array():
       return JSVArray(v)
    # TODO: Deal with case where in v is an object
    

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

    def __on_evaluate__(self, obj, result, _):
        try:
            value = self.webview.evaluate_javascript_finish(result)
        except Exception as err:
            error(err)
            return
        eval_id = value.object_get_property_at_index(0).to_int32()
        self._evaluate_list[eval_id](jsv_to_primitive(value.object_get_property_at_index(1)))
        del self._evaluate_list[eval_id]


    def apply_stylesheet(self, css=""):
        if css == "":
            warn("apply_stylesheet() called with no source code")
            return
        self.webucm.add_style_sheet(WebKit2.UserStyleSheet(css, 0, 0, None, None)) 

    NOP = lambda x: None

    def evaluate(self, js="", ondone=NOP):
        if js == "":
            warn("evaluate() called with no source code")
            return
        eval_id = self._eval_cnt
        if ondone != self.NOP:
            js = f"[{eval_id}, ({js})]"
            # warn(js)
            self._evaluate_list[eval_id] = ondone
            self.webview.evaluate_javascript(js, len(js), None, None, None, self.__on_evaluate__, None)
            self._eval_cnt += 1
        else:
            self.webview.evaluate_javascript(js, len(js), None, None, None, self.NOP, None)
            warn(js)

    def onload(self, fn, noOfTimes = float('inf')):
        self._onload_listeners.append([fn, noOfTimes])

    def _onload(self, _, evt):
        if evt == self.LOAD_FINISHED:
            for idx in range(0, len(self._onload_listeners)):
                if self._onload_listeners[idx][1] > 0:
                    self._onload_listeners[idx][0]()
                self._onload_listeners[idx][1] -= 1


    def register_hander(self, name, onmessage=NOP):
        self.webucm.register_script_message_handler(name)
        self.webucm.connect(f"script-message-received::{name}", lambda _, x: onmessage(jsv_to_primitive(x.get_js_value())))


    def __init__(self, window_type_hint=Gdk.WINDOW_TYPE_HINT_NORMAL, inspect=False, transparent=False, html=None, forward_console=True, window_css="", persistent=None, decorated=True, exit_on_window_close=True, title="Webview", visible=True, url=None, window_type=Gdk.WindowTypeHint.DIALOG, position=Gtk.WindowPosition.CENTER, size=(800, 600)):
        self.window = Gtk.Window(title=title, type_hint=window_type, decorated=decorated)
        self.window.set_position(position)
        self.window.set_default_size(size[0], size[1])
        self.webview = WebKit2.WebView()

        if transparent:
            self.window.set_visual(self.window.get_screen().get_rgba_visual())
            self.webview.set_background_color(Gdk.RGBA(0,0,0,0)) # Set webview background transparent
            window_css += "window { background-color: rgba(0,0,0,0); }"

        if window_css:
            style_provider = Gtk.CssProvider()
            style_provider.load_from_data(window_css)
            Gtk.StyleContext.add_provider_for_screen(self.window.get_screen(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.webcfg = self.webview. get_settings()
        self.webcfg.set_enable_write_console_messages_to_stdout(forward_console)
        self.webcfg.set_allow_universal_access_from_file_urls(True)
        self.webcfg.set_allow_file_access_from_file_urls(True)
        self.webcfg.set_enable_developer_extras(True)
        self.webview.set_settings(self.webcfg)
        
        if url:
            self.webview.load_uri(url)

        if html:
            self.webview.load_html(html, "file://")

        self.webctx = self.webview.get_context()
        self.webucm = self.webview.get_user_content_manager()

        if persistent:
            self._store_session = persistent[0] 
            cookie_manager = self.webctx.get_cookie_manager()
            cookie_manager.set_persistent_storage(persistent[1], WebKit2.CookiePersistentStorage.TEXT)

        if inspect:
            inspector = self.webview.get_inspector()
            inspector.show()

        self.window.add(self.webview)

        if exit_on_window_close:
            self.window.connect("destroy", Gtk.main_quit)

        self.webview.connect('load-changed', self._onload)

        if visible:
            self.window.show_all()

    def __enter__(self):
        return self

    def __exit__(self):
        if self._store_session:
            session_state = self.webview.get_session_state()
            session_state_data = session_state.serialize().get_data()

            with open(self._store_session, "wb") as f:
               f.write(session_state_data)

    def run(self):
        Gtk.main()


