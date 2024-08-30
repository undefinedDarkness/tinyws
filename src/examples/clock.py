from ..tinyws import Webview
import pathlib

script_dir = pathlib.Path(__file__).parent.resolve()
wv = Webview(forward_console=True, decorated=False, transparent=True, inspect=False, width=800, height=300,
html="""

<!DOCTYPE HTML>
<html>
<head>
<style>
    html, body {
        background: rgba(0,0,0,0);
        color: #f0f0f0;
        margin: 0;
        padding: 0;
        font-family: system-ui;
    }
    
    body {
    	display: flex;
    	justify-content: center;
    	align-items: center;
    	flex-direction: column;
    }

    .cp_embed_wrapper {
        width: 100%;
        height: 100%:
    }
</style>
</head>
<body>
<p data-height="300" data-theme-id="24311" data-slug-hash="poXjwaK" data-default-tab="result" data-user="triss90" data-embed-version="2" class="codepen">See the Pen <a href="https://codepen.io/triss90/pen/gMwRXQ/">Simplistic Dialog</a> by Tristan  White (<a href="https://codepen.io/triss90">@triss90</a>) on <a href="https://codepen.io">CodePen</a>.</p>
<script async src="https://assets.codepen.io/assets/embed/ei.js"></script>
</body>
</html>

""")


wv.run()
