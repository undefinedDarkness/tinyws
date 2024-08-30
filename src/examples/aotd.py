from ..tinyws import Webview
from logging import info, warning, error
import logging

# You can use the Nasa API too but this is to demonstrate running javascript
# `https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY`

wv = Webview(url="https://apod.nasa.gov/apod/astropix.html", decorated=False)


def onload():
    wv.register_handler(r"""(() => {
                const image = document.querySelector(' a > img ')
                image.parentNode.click()
                return [ image.naturalWidth, image.naturalHeight ]
    })()""", lambda dim: wv.window.resize(dim[0], dim[1]))


logging.basicConfig(level=logging.INFO)
wv.onload(onload, 1)

wv.run()
