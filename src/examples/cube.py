from ..tinyws import Webview
import pathlib

script_dir = pathlib.Path(__file__).parent.resolve()
wv = Webview(inspect=True, decorated=False, transparent=True, width='512', height='512', html=f"""

<!DOCTYPE HTML>
<html>
<head>
<style>
    html {{
      background: rgba(255,255,255,0.35);
      border-radius: 8px;
    }}

    body {{
        background: transparent;
    }}

    html, body {{
        color: #f0f0f0;
        padding: 0;
        margin: 0;
        height: 100%;
        max-width: 100%;
    }}

</style>
</head>
<body>

<div style="margin: 0 4em;" id="content">
    <img style="max-width: 80vw;" src="file://{script_dir}/assets/wall-gtk4.svg" />
    <h1 style="white-space: nowrap;">TinyWS: Hello World 🍜 </h1>
</div>

</body>
</html>

""")


wv.run()
