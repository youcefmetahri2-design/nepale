NETGUARD AI — Windows network connection notifier

FEATURES
- Monitors locally visible TCP/UDP internet endpoints.
- Detects newly observed ESTABLISHED and SYN_SENT connections.
- Shows a Windows-style popup with process name, PID, remote IP:port and time.
- Keeps a recent activity list and basic counters.
- Pause/resume and clear history.

IMPORTANT LIMITATIONS
- This is a local connection monitor, not a firewall. It does not block connections.
- It polls once per second, so very short connections may be missed.
- Windows may restrict process/connection details. Run as Administrator for the best
  visibility. Even elevated, some system processes may not expose full details.
- It does not inspect packet contents, passwords, messages, browser pages, or cookies.
- No AI cloud service is involved; "AI" is the product name only.

BUILD A READY EXE USING GITHUB ACTIONS
1. Sign in at https://github.com and create a new repository.
2. Upload ALL contents of this folder, including the hidden .github folder.
   Ensure the workflow file path is .github/workflows/build-windows.yml.
3. Open the repository's Actions tab.
4. Select "Build NetGuard AI Windows EXE" and click "Run workflow".
   (A push to the main branch also starts a build.)
5. Open the completed green workflow run.
6. Under Artifacts, download "NetGuard_AI-Windows".
7. Extract the downloaded ZIP to find NetGuard_AI.exe.

RUN
Double-click NetGuard_AI.exe. If the process list looks incomplete, close it and
right-click the EXE > Run as administrator.
