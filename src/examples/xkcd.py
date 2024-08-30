from tinyws import Webview
from logging import info, warning, error
import logging
import requests

wv = Webview(html="""

<!DOCTYPE html>
<html>
<head>
<style>
* { margin: 0; padding: 0; }
</style>
</head>
<body>
<img id='xkcd' />
<script>

function loadImage(obj) {
            const image = document.querySelector('#xkcd');
            image.setAttribute('src', obj.img)
            image.setAttribute('title', obj.alt)
            image.onload = () => { window.webkit.messageHandlers.sys.postMessage([image.naturalWidth, image.naturalHeight]) }
}

</script>
</body>
</html>

""", decorated=False, visible=False)

xkcd = requests.get("https://xkcd.com/info.0.json").text
def onload(_, event):
    global xkcd
    if event == Webview.LOAD_FINISHED:
        wv.register_handler(f"loadImage({ xkcd })")

def onResizeRequest(x):
    wv.window.resize(x[0], x[1])
    wv.window.show_all()

wv.register_handler("sys", onResizeRequest)

wv.webview.connect("load-changed", onload)

wv.run()
