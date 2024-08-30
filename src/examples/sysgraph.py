from ..tinyws import Webview
from ..tinyws.capabilities.sysinfo import SystemInfoCapability
from ..tinyws.capabilities import HelloCapability

def generate_html():
    with open(__file__.rsplit('/', 1)[0] + '/sysgraph.html') as f:
        return f.read()

def main():
    # Create the Webview and load HTML
    capabilities = [SystemInfoCapability(), HelloCapability()]
    webview = Webview(title="System Monitor", html=generate_html(), capabilities=capabilities, inspect=True)
    
    # Start the GTK main loop
    webview.run()

if __name__ == "__main__":
    main()
