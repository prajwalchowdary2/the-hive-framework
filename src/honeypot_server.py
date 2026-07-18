import http.server
import socketserver
import datetime
import os
import io
import zipfile
import sys
import subprocess

PORT = 8080
LOG_FILE = "data/honeypot_alerts.log"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# ANSI Colors for massive terminal alerts
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG_RED = "\033[41m"
WHITE = "\033[97m"

def trigger_alarm(client_ip, user_agent, path):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Write to stealth log
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] INTRUSION DETECTED | IP: {client_ip} | PATH: {path} | UA: {user_agent}\n")

    # 2. Trigger massive terminal alert
    sys.stdout.write("\a") # Bell sound if supported
    print(f"\n{BG_RED}{WHITE}{BOLD}")
    print("===============================================================================")
    print("                      ! ! ! INTRUSION DETECTED ! ! !                           ")
    print("===============================================================================")
    print(f"{RESET}{RED}{BOLD}")
    print(f" HONEYPOT TRIGGERED ")
    print(f" TIME         : {timestamp}")
    print(f" ATTACKER IP  : {client_ip}")
    print(f" TARGET PATH  : {path}")
    print(f" USER-AGENT   : {user_agent}")
    print(f" ACTION       : Decoy Sigma Rules Accessed")
    print("===============================================================================")
    print(f"{RESET}\n")

def create_fake_zip():
    # Creates a tiny, valid but empty zip file in memory to send back to the attacker
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sigma_rules.txt", "NICE TRY.")
    buf.seek(0)
    return buf.read()

class HoneypotHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        # Handle fetching the latest real run
        if self.path == '/api/latest_run':
            import glob
            import json
            
            output_dir = "output"
            if not os.path.exists(output_dir):
                self.send_error(404, "No output directory found")
                return
                
            runs = sorted(glob.glob(os.path.join(output_dir, "run_*")), key=os.path.getmtime, reverse=True)
            if not runs:
                self.send_error(404, "No runs found")
                return
                
            latest_run = runs[0]
            results_path = os.path.join(latest_run, "raw_results.json")
            
            if not os.path.exists(results_path):
                self.send_error(404, "raw_results.json not found in latest run")
                return
                
            with open(results_path, "r", encoding="utf-8") as f:
                data = f.read()
                
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
            return
            
        # Serve normal GET requests to render the dashboard flawlessly
        super().do_GET()

    def do_POST(self):
        # 1. Handle Simulation Trigger
        if self.path == '/api/run_simulation':
            print(f"[*] Frontend UI Simulation Sequence Triggered.")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "simulating"}')
            return

        # 2. Handle Honeypot Trap
        elif self.path == '/api/download/sigma_rules.zip':
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            # Fire the alarm!
            trigger_alarm(client_ip, user_agent, self.path)
            
            # Serve the fake zip file
            fake_zip = create_fake_zip()
            self.send_response(200)
            self.send_header("Content-type", "application/zip")
            self.send_header("Content-Length", str(len(fake_zip)))
            self.send_header("Content-Disposition", 'attachment; filename="hive_sigma_rules_export.zip"')
            self.end_headers()
            self.wfile.write(fake_zip)
        else:
            self.send_error(404, "File not found")

    # Suppress standard logging to keep the terminal clean until an alert hits
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print(f"{BOLD}THE HIVE - Honeypot & Dashboard Server{RESET}")
    print(f"Starting server on port {PORT}...")
    print(f"Honeypot Trap is [ ACTIVE ]")
    print(f"Dashboard available at http://localhost:{PORT}/dashboard.html\n")
    
    with socketserver.TCPServer(("", PORT), HoneypotHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Honeypot server.")
