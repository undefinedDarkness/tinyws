import Xlib.display
from Xlib import X
from Xlib.protocol import event
import threading
import time
from typing import Dict, Any
from ..utils.logger import info
from .. import Webview
from . import Capability, export #, EventCapability
from .events import EventCapability

class X11WindowTreeCapability(EventCapability):
    @staticmethod
    def name() -> str:
        return "x11WindowTree"

    def __init__(self):
        super().__init__()
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root
        self.tree = {}
        self.monitoring = False

    @export
    def getWindowTree(self):
        self.update_tree()
        return self.tree

    def update_tree(self):
        self.tree = self._get_window_tree(self.root)

    def _get_window_tree(self, window):
        try:
            children = window.query_tree().children
            if not children:
                return None

            workspace_windows = {}
            for child in children:
                try:
                    workspace = self._get_window_workspace(child)
                    if workspace not in workspace_windows:
                        workspace_windows[workspace] = []
                    window_name = self._get_window_name(child)
                    if window_name:
                        workspace_windows[workspace].append(window_name)
                except Xlib.error.BadWindow:
                    continue

            return workspace_windows
        except Xlib.error.BadWindow:
            return None

    def _get_window_workspace(self, window):
        try:
            workspace = window.get_full_property(self.display.intern_atom('_NET_WM_DESKTOP'), 0)
            if workspace:
                return f"Workspace {workspace.value[0] + 1}"
            return "Unknown Workspace"
        except Xlib.error.BadWindow:
            return "Unknown Workspace"

    def _get_window_name(self, window):
        try:
            name = window.get_wm_name()
            return name if name else None
        except Xlib.error.BadWindow:
            return None

    @export
    def startMonitoring(self, wv: Webview):
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor_changes, args=(wv,), daemon=True).start()
            info("Started monitoring X11 window changes")

    @export
    def stopMonitoring(self):
        self.monitoring = False
        info("Stopped monitoring X11 window changes")

    def _monitor_changes(self, wv: Webview):
        self.root.change_attributes(event_mask=X.SubstructureNotifyMask)
        while self.monitoring:
            event = self.display.next_event()
            if isinstance(event, (Xlib.protocol.event.CreateNotify, Xlib.protocol.event.DestroyNotify)):
                self.update_tree()
                self.emit_event(wv, "windowTreeUpdated", {"tree": self.tree})
            time.sleep(0.1)  # Prevent high CPU usage

    def register(self, wv: Webview):
        super().register(wv)
        # Additional setup if needed
        info(f"X11WindowTreeCapability registered successfully!")
