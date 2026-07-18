import webview
import threading
import socketserver
import time
import sys
import os

# Import our custom honeypot server handler
# Ensure we are in the correct directory so it can find src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.honeypot_server import HoneypotHandler, PORT

def start_honeypot_server():
    """Starts the Honeypot HTTP server in a background thread."""
    # Allow address reuse so it doesn't crash if previously left open
    socketserver.TCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.TCPServer(("", PORT), HoneypotHandler)
        print(f"[*] Background Honeypot Server active on port {PORT}")
        httpd.serve_forever()
    except Exception as e:
        print(f"[!] Error starting server: {e}")

if __name__ == '__main__':
    # 1. Start the Honeypot server in a background thread
    server_thread = threading.Thread(target=start_honeypot_server, daemon=True)
    server_thread.start()

    # 2. Give the server a moment to bind to the port
    time.sleep(1)

    # 3. Create the Native Desktop Window
    print("[*] Launching THE HIVE native desktop interface...")
    
    # We set the background color to match the Obsidian theme (#0a0606)
    # so there is no white flash while the HTML loads.
    window = webview.create_window(
        title='THE HIVE — Advanced Emulation', 
        url=f'http://localhost:{PORT}/dashboard.html',
        width=1400, 
        height=900,
        resizable=True,
        background_color='#0a0606', 
        text_select=False
    )

    # 4. Start the WebView Application Loop
    webview.start()
