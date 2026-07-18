#!/usr/bin/env python3
"""Generate a LaTeX-style academic PDF for The Hive Technical Report."""

import os
import sys

# Fix encoding for Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fpdf import FPDF

class AcademicPDF(FPDF):
    """Custom PDF class with LaTeX-style academic formatting."""

    def __init__(self):
        super().__init__(format='A4')
        self.set_auto_page_break(auto=True, margin=25)
        self.section_num = 0
        
        # Add Unicode fonts from Windows system
        font_dir = "C:/Windows/Fonts"
        self.add_font("Serif", "", f"{font_dir}/georgia.ttf", uni=True)
        self.add_font("Serif", "B", f"{font_dir}/georgiab.ttf", uni=True)
        self.add_font("Serif", "I", f"{font_dir}/georgiai.ttf", uni=True)
        self.add_font("Serif", "BI", f"{font_dir}/georgiaz.ttf", uni=True)
        self.add_font("Mono", "", f"{font_dir}/consola.ttf", uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Serif", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "The Hive: Deep Technical Execution Report", align="C")
            self.ln(3)
            self.set_draw_color(180, 180, 180)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Serif", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, str(self.page_no()), align="C")

    def title_block(self, title, subtitle):
        self.set_font("Serif", "B", 18)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 9, title, align="C")
        self.ln(4)
        
        self.set_font("Serif", "", 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, subtitle, align="C")
        self.ln(8)
        
        self.set_draw_color(180, 180, 180)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(8)

    def section(self, title):
        self.section_num += 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        num = roman[self.section_num - 1] if self.section_num <= 10 else str(self.section_num)
        self.ln(4)
        self.set_font("Serif", "B", 13)
        self.set_text_color(20, 20, 20)
        self.cell(0, 8, f"{num}. {title}")
        self.ln(8)

    def subsection(self, title):
        self.ln(3)
        self.set_font("Serif", "BI", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, title)
        self.ln(7)

    def body_text(self, text, indent=False):
        self.set_font("Serif", "", 10)
        self.set_text_color(30, 30, 30)
        if indent:
            self.set_x(self.l_margin + 8)
            self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5.5, text, align="J")
        else:
            self.multi_cell(0, 5.5, text, align="J")
        self.ln(3)

    def bold_text(self, text):
        self.set_font("Serif", "B", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text, align="J")
        self.ln(1)

    def highlight_box(self, title, text):
        self.set_fill_color(249, 249, 240)
        self.set_draw_color(201, 162, 39)
        self.set_line_width(0.6)
        x = self.l_margin
        y = self.get_y()
        w = self.w - self.l_margin - self.r_margin
        
        self.set_x(x + 5)
        self.set_font("Serif", "B", 9)
        self.set_text_color(20, 20, 20)
        self.cell(w - 10, 5, title, align="L")
        self.ln(5)
        
        self.set_x(x + 5)
        self.set_font("Serif", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(w - 10, 4.5, text, align="L")
        
        h = self.get_y() - y + 4
        self.rect(x, y - 2, w, h, style="D")
        self.line(x, y - 2, x, y - 2 + h)
        self.ln(6)

    def bullet_point(self, title, text):
        self.set_font("Serif", "B", 10)
        self.set_text_color(30, 30, 30)
        
        x = self.l_margin + 5
        self.set_x(x)
        self.write(5.5, "\u2022  " + title + ": ")
        
        self.set_font("Serif", "", 10)
        self.write(5.5, text)
        self.ln(6)


def generate_pdf():
    pdf = AcademicPDF()
    pdf.set_title("The Hive: Deep Technical Execution Report")
    pdf.set_author("The Hive Automated Platform")
    pdf.add_page()

    # ---- TITLE ----
    pdf.title_block(
        "The Hive: Deep Technical Execution Report",
        "Mechanics, Artifacts, and Detection of Emulated ATT&CK Techniques"
    )

    pdf.body_text(
        "This technical report breaks down exactly how The Hive mathematically models and technically executes "
        "Advanced Persistent Threat (APT) behavior. It details the precise commands run by the Operator Fleet, "
        "the forensic artifacts left on the target system, and the telemetry analyzed by the Purple Team Agent."
    )
    pdf.body_text(
        "The following breakdown is based on the 12 specific techniques extracted during the APT29 "
        "(Cozy Bear) emulation profile."
    )

    # ---- PHASE 1 ----
    pdf.section("Phase 1: Reconnaissance (Network & Host Discovery)")
    
    pdf.subsection("1. T1082 - System Information Discovery")
    pdf.highlight_box("Adversary Goal", "Determine OS version, hardware configurations, and patch levels to tailor local privilege escalation exploits.")
    pdf.bullet_point("Hive Execution Mechanism", "The Recon Agent executes native Windows API calls and WMI queries, specifically running: systeminfo, wmic os get /format:list, and Get-ComputerInfo.")
    pdf.bullet_point("Forensic Footprint", "Spawning of wmic.exe and systeminfo.exe from anomalous parent processes (e.g., powershell.exe rather than explorer.exe).")
    pdf.bullet_point("Purple Team Detection Logic", "Generates a Sigma rule looking for rapid, successive execution of built-in discovery binaries (Event ID 4688 Process Creation) within a narrow 5-second timeframe.")

    pdf.subsection("2. T1018 - Remote System Discovery")
    pdf.highlight_box("Adversary Goal", "Enumerate active hosts on the subnet to identify targets for lateral movement (e.g., Domain Controllers, File Servers).")
    pdf.bullet_point("Hive Execution Mechanism", "Uses nltest /domain_trusts, net view /domain, and active ICMP/ARP sweeps via PowerShell Test-NetConnection.")
    pdf.bullet_point("Forensic Footprint", "High volume of ARP requests from a single endpoint; execution of nltest.exe querying Domain Trusts.")
    pdf.bullet_point("Purple Team Detection Logic", "Sigma rule targeting nltest.exe command-line arguments specifically querying trust relationships, which is highly unusual for standard user behavior.")

    pdf.subsection("3. T1016 - System Network Configuration Discovery")
    pdf.highlight_box("Adversary Goal", "Identify network topology, routing tables, and active network connections.")
    pdf.bullet_point("Hive Execution Mechanism", "The agent runs ipconfig /all, arp -a, and route print.")
    pdf.bullet_point("Forensic Footprint", "Execution of these utilities in quick succession.")
    pdf.bullet_point("Purple Team Detection Logic", "D3FEND mapping to Network Traffic Analysis; looking for arp.exe execution combined with outbound network scanning behavior.")

    # ---- PHASE 2 ----
    pdf.section("Phase 2: Initial Access & Execution")

    pdf.subsection("4. T1566.001 - Spearphishing Attachment")
    pdf.highlight_box("Adversary Goal", "Trick a user into opening a malicious document, establishing the initial foothold.")
    pdf.bullet_point("Hive Execution Mechanism", "The Access Agent drops an inert, macro-enabled Word document (.docm) or an LNK shortcut disguised as a PDF onto the file system, then simulates a user click via ShellExecute.")
    pdf.bullet_point("Forensic Footprint", "WINWORD.EXE spawning child processes like cmd.exe or powershell.exe.")
    pdf.bullet_point("Purple Team Detection Logic", "Hard Sigma rule targeting Microsoft Office applications acting as parent processes to command-line interpreters (Suspicious Process Lineage).")

    pdf.subsection("5. T1059.001 - Command and Scripting Interpreter: PowerShell")
    pdf.highlight_box("Adversary Goal", "Execute malicious payloads natively in memory without touching the disk (Fileless execution).")
    pdf.bullet_point("Hive Execution Mechanism", "Executes a Base64 encoded payload: powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand <BASE64_STRING>")
    pdf.bullet_point("Forensic Footprint", "PowerShell Script Block Logging (Event ID 4104) capturing the decoded script; powershell.exe running with hidden window arguments.")
    pdf.bullet_point("Purple Team Detection Logic", "YARA rule targeting the Base64 decoding stubs; Sigma rule flagging ExecutionPolicy Bypass and -EncodedCommand flags.")

    pdf.subsection("6. T1053.005 - Scheduled Task")
    pdf.highlight_box("Adversary Goal", "Execute code at a specific time or under a specific system context (SYSTEM privileges).")
    pdf.bullet_point("Hive Execution Mechanism", "The agent registers a task via the schtasks.exe binary: schtasks /create /tn \"WindowsUpdateCore\" /tr \"C:\\Temp\\payload.exe\" /sc onstart /ru SYSTEM")
    pdf.bullet_point("Forensic Footprint", "Windows Security Event ID 4698 (A scheduled task was created).")
    pdf.bullet_point("Purple Team Detection Logic", "Rule alerting on any Scheduled Task creation where the binary path points to C:\\Users\\* or C:\\Temp\\* instead of C:\\Windows\\System32.")

    pdf.subsection("7. T1027 - Obfuscated Files or Information")
    pdf.highlight_box("Adversary Goal", "Evade signature-based antivirus detection by hiding the true nature of the payload.")
    pdf.bullet_point("Hive Execution Mechanism", "The payload is XOR-encrypted or packed using a custom stub before being written to disk or memory.")
    pdf.bullet_point("Forensic Footprint", "High entropy files written to disk; AMSI (Antimalware Scan Interface) bypass attempts in memory.")
    pdf.bullet_point("Purple Team Detection Logic", "YARA rule analyzing file entropy; if entropy exceeds 7.2 (highly packed/encrypted), it flags the file for dynamic analysis.")

    pdf.subsection("8. T1070.004 - File Deletion")
    pdf.highlight_box("Adversary Goal", "Remove forensic evidence (droppers, configuration files) to hinder incident response.")
    pdf.bullet_point("Hive Execution Mechanism", "Uses Remove-Item -Force or native SDelete (Sysinternals) to wipe staging directories.")
    pdf.bullet_point("Forensic Footprint", "Sysmon Event ID 11 (File Create) followed rapidly by Sysmon Event ID 23 (File Delete) or Event ID 26 (File Delete logged).")
    pdf.bullet_point("Purple Team Detection Logic", "Alerts on the execution of sdelete.exe or rapid creation-and-deletion cycles of executable files in temporary directories.")

    # ---- PHASE 3 ----
    pdf.section("Phase 3: Persistence")

    pdf.subsection("9. T1547.001 - Registry Run Keys / Startup Folder")
    pdf.highlight_box("Adversary Goal", "Ensure the malware automatically executes every time the machine reboots or the user logs in.")
    pdf.bullet_point("Hive Execution Mechanism", "The Persistence Agent executes: reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /v \"OneDriveSync\" /t REG_SZ /d \"C:\\Users\\Public\\payload.exe\" /f")
    pdf.bullet_point("Forensic Footprint", "Sysmon Event ID 13 (Registry Event - Value Set) modifying the Run or RunOnce keys.")
    pdf.bullet_point("Purple Team Detection Logic", "High-confidence Sigma rule alerting on any modification to HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run by non-system processes like powershell.exe or cmd.exe.")

    # ---- PHASE 4 ----
    pdf.section("Phase 4: Lateral Movement")

    pdf.subsection("10. T1550.002 - Pass the Hash")
    pdf.highlight_box("Adversary Goal", "Authenticate to remote servers without knowing the plaintext password, using a stolen NTLM hash.")
    pdf.bullet_point("Hive Execution Mechanism", "The Movement Agent simulates Mimikatz-style PtH by injecting an NTLM hash into the LSASS process and requesting a Kerberos TGT or NTLM authentication to \\\\DC01\\C$.")
    pdf.bullet_point("Forensic Footprint", "Windows Security Event ID 4624 (Logon) with Logon Type 9 (NewCredentials) matching the stolen account, followed by SMB connections.")
    pdf.bullet_point("Purple Team Detection Logic", "Detects Event ID 4624 (Logon Type 9) originating from abnormal processes; monitors lsass.exe memory access (Sysmon Event ID 10) by suspicious binaries.")

    pdf.subsection("11. T1021.002 - SMB/Windows Admin Shares")
    pdf.highlight_box("Adversary Goal", "Move binary payloads to remote servers and execute them via native administrative protocols.")
    pdf.bullet_point("Hive Execution Mechanism", "Copies a payload over port 445: copy payload.exe \\\\FS01\\C$\\Windows\\Temp\\ and executes it remotely via WMI or PsExec.")
    pdf.bullet_point("Forensic Footprint", "Sysmon Event ID 3 (Network Connection) on port 445; Event ID 5140 (A network share object was accessed) specifically targeting ADMIN$ or C$.")
    pdf.bullet_point("Purple Team Detection Logic", "Alerts on workstation-to-workstation SMB traffic over port 445 (standard environments should only see workstation-to-server traffic).")

    # ---- PHASE 5 ----
    pdf.section("Phase 5: Exfiltration")

    pdf.subsection("12. T1048.002 - Exfiltration Over Asymmetric Encrypted Non-C2 Protocol")
    pdf.highlight_box("Adversary Goal", "Steal sensitive data while blending in with normal corporate web traffic to bypass DPI (Deep Packet Inspection).")
    pdf.bullet_point("Hive Execution Mechanism", "The Exfil Agent collects files into a password-protected .zip archive, then pushes the data out via HTTPS (Port 443) to a cloud storage provider (e.g., AWS S3, Mega, or a custom VPS).")
    pdf.bullet_point("Forensic Footprint", "Large, sustained outbound network connections over port 443 from non-browser processes (e.g., curl.exe or powershell.exe).")
    pdf.bullet_point("Purple Team Detection Logic", "Sigma rule looking for byte transfers exceeding 50MB in a single HTTPS session originating from anomalous processes. D3FEND mapping points to implementing strict outbound proxy filtering.")

    # Save
    output_path = os.path.join(os.path.dirname(__file__), "The_Hive_Technical_Report.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")

if __name__ == "__main__":
    generate_pdf()
