from logging import critical
from typing import Callable, Dict, Any
import json
from ..utils.logger import info, warn, error
from .. import Webview
import traceback


def export(fn):
    fn.__exported__ = fn.__name__
    return fn


class Capability:
    @staticmethod
    def name() -> str:
        raise NotImplementedError("Must be implemented in subclass")

    __exported_methods__: Dict[str, Callable] = {}
    wv: Webview

    def __init__(self) -> None:
        self.__exported_methods__ = {}

    def __register__(self, wv: Webview):
        self.wv = wv
        for kName in dir(self):
            v = getattr(self, kName)
            if hasattr(v, "__exported__"):
                self.__exported_methods__[v.__exported__] = v

        # Register message handler
        wv.register_handler(name=self.name(), onmessage=self.__on_message__)

        # Create JS object with all exported methods
        js_methods = ", ".join(
            f"""
{name}: (...args) => new Promise((resolve, reject) => {{
    const callbackId = crypto.randomUUID();  // Generate a unique callback ID
    window.capabilities["{self.name()}"].__callbacks[callbackId] = {{
        resolve: resolve,
        reject: reject
    }};
    window.webkit.messageHandlers['{self.name()}'].postMessage({{
        method: '{name}',
        args: args,
        callbackId: callbackId
    }})
}})
"""
            for name in self.__exported_methods__
        )

        # Register JavaScript side
        wv.evaluate(f"""
        (() => {{
            window.capabilities = window.capabilities ?? {{}}
            window.capabilities["{self.name()}"] = {{
                __callbacks: {{}},
                {js_methods}
            }};
            console.log(`[tinyws] Capability {self.name()} was successfully loaded!`)
            // window.capabilities['hello'].getTimestamp().then(v => {{
            //    console.log(+Date.now() - v, " millisecond communication between Py and Js")
            // }})
        }})()
        """)
        info(f"Capability '{self.name()}' was successfully loaded!")

    def __on_message__(self, v):
        method_name = v.get("method")
        args = v.get("args", [])
        callback_id = v.get("callbackId")

        try:
            if method_name in self.__exported_methods__:
                fn = self.__exported_methods__[method_name]
                # print("Calling function " + method_name + " with args: ")
                # __import__('pprint').pprint(args)
                result = fn(self, *args)
                self.__send_response(callback_id, result)
        except Exception as e:
            err = str(e)
            critical(f"Error in method '{method_name}': {str(e)}")
            error(traceback.format_exc())
            self.__send_response(callback_id, None, err)

    def __send_response(self, callback_id, result=None, error=None):
        # This function sends the response back to JavaScript
        js_code = f"""
        (() => {{
            const callback = window.capabilities["{self.name()}"].__callbacks['{callback_id}'];
            if (callback) {{
                if ({json.dumps(error)} !== null) {{
                    callback.reject({json.dumps(error)});
                }} else {{
                    callback.resolve({json.dumps(result)});
                }}
                delete window.capabilities["{self.name()}"].__callbacks['{callback_id}'];
            }}
        }})()
        """
        self.wv.evaluate(js_code)  # Send the response back to the JavaScript side


class HelloCapability(Capability):
    @staticmethod
    def name() -> str:
        return "hello"

    @export
    def getTimestamp(self, v):
        import time
        return time.time() * 1000

    @export
    def pprint(self, v):
        __import__("pprint").pprint(v)

    @export
    def sayHello(self, helloFrom: str):
        print(f"Hello from {helloFrom}")
