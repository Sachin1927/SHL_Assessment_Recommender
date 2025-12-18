import subprocess
import sys
import time
import os
import signal

def run_project():
    print(" Starting SHL Assessment System...")
    print("---------------------------------------")

    # 1. Start the Backend API (using the current Python environment)
    # We use "-m src.api" to avoid the ModuleNotFoundError you saw earlier
    print("🔹 Launching Backend API...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "src.api"],
        env=os.environ.copy()
    )

    # Give the API a few seconds to start up before launching the frontend
    print(" Waiting for API to initialize...")
    time.sleep(4)

    # 2. Start the Frontend (Streamlit)
    print("🔹 Launching Frontend UI...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend.py"],
        env=os.environ.copy()
    )

    print("---------------------------------------")
    print(" System Running! Press Ctrl+C to stop.")
    print("---------------------------------------")

    try:
        # Keep the script running to monitor the processes
        api_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        # 3. Handle Exit (Ctrl+C)
        print("\n Shutting down processes...")
        api_process.terminate()
        frontend_process.terminate()
        print(" Goodbye!")

if __name__ == "__main__":
    run_project()