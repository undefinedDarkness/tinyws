from typing import Type, Dict, Any
from ..utils.logger import info
from .. import Webview
from . import Capability, export
import json

class EventCapability(Capability):
    def __init__(self):
        super().__init__()
        self._listeners: Dict[str, list] = {}

    @staticmethod
    def name() -> str:
        raise NotImplementedError("Must be implemented in subclass")

    def __register__(self, wv: Webview):
        super().__register__(wv)

        # Create EventTarget on JavaScript side
        wv.evaluate(f"""(() => {{
            class {self.name()}EventTarget extends EventTarget {{
                constructor() {{
                    super();
                }}
            }}
            window.capabilities["{self.name()}"].eventTarget = new {self.name()}EventTarget();
            window.capabilities["{self.name()}"].addEventListener = (type, listener) => {{
                window.capabilities["{self.name()}"].eventTarget.addEventListener(type, listener);
            }};
            window.capabilities["{self.name()}"].removeEventListener = (type, listener) => {{
                window.capabilities["{self.name()}"].eventTarget.removeEventListener(type, listener);
            }};
            console.log(`[tinyws] {self.name()}EventTarget created successfully!`);
        }})();""")

    @export
    def addEventListener(self, event_type: str, listener_id: str):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener_id)
        info(f"Added listener {listener_id} for event {event_type}")

    @export
    def removeEventListener(self, event_type: str, listener_id: str):
        if event_type in self._listeners and listener_id in self._listeners[event_type]:
            self._listeners[event_type].remove(listener_id)
            info(f"Removed listener {listener_id} for event {event_type}")

    def emit_event(self, wv: Webview, event_type: str, detail: Dict[str, Any] = None):
        if not detail:
            detail = {}
        js_detail = json.dumps(detail)
        wv.evaluate(f"""
            const event = new CustomEvent("{event_type}", {{ detail: {js_detail} }});
            window.capabilities["{self.name()}"].eventTarget.dispatchEvent(event);
        """)
        info(f"Emitted event {event_type} with detail: {detail}")

class ExampleEventCapability(EventCapability):
    @staticmethod
    def name() -> str:
        return "exampleEvent"

    @export
    def triggerCustomEvent(self, wv: Webview, event_name: str, data: Dict[str, Any]):
        self.emit_event(wv, event_name, data)