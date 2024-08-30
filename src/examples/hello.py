from ..tinyws import Webview
import pathlib

script_dir = pathlib.Path(__file__).parent.resolve()
wv = Webview(decorated=False, transparent=True,
html=f"""

<!DOCTYPE HTML>
<html>
<head>
<style>
    html, body {{
        background: rgba(0,0,0,0);
        color: #f0f0f0;
        font-family: system-ui;
    }}
    
    body {{
    	display: flex;
    	justify-content: center;
    	align-items: center;
    	flex-direction: column;
    }}
</style>
</head>
<body>

    <img src="file://{script_dir}/assets/emma.webp" />
    <h1 style="font-size: 5em;">Hello World!</h1>

</body>
</html>

""")


wv.run()
