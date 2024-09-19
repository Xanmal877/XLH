import os
import platform

def is_windows():
    return platform.system() == 'Windows'

def create_update_script():
    if is_windows():
        script_content = """@echo off

REM Create a virtual environment named XLHenv
python -m venv venv

REM Activate the virtual environment
call venv\\Scripts\\activate

REM Install the required packages from piplist.txt
pip install wheel
pip install -r piplist.txt

REM Check for CUDA compatibility and install the correct version of torch
python -c "import torch; print('CUDA available' if torch.cuda.is_available() else 'CUDA not available')"
if %errorlevel%==0 (
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    pip install torch torchvision torchaudio
)

REM Notify the user
echo Setup complete.
pause
"""
        with open("update.bat", "w") as bat_file:
            bat_file.write(script_content)
    else:
        script_content = """#!/bin/bash

# Create a virtual environment named XLHenv
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages from piplist.txt
pip install wheel
pip install -r piplist.txt

# Check for CUDA compatibility and install the correct version of torch
if python3 -c "import torch; print('CUDA available' if torch.cuda.is_available() else 'CUDA not available')" | grep -q "CUDA available"; then
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    pip install torch torchvision torchaudio
fi

# Notify the user
echo "Setup complete."
"""
        with open("update.sh", "w") as sh_file:
            sh_file.write(script_content)
        os.chmod("update.sh", 0o755)

def create_run_script():
    if is_windows():
        script_content = """@echo off

call venv\\Scripts\\activate

python main.py
pause
"""
        with open("run.bat", "w") as bat_file:
            bat_file.write(script_content)
    else:
        script_content = """#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the main Python script
python main.py
"""
        with open("run.sh", "w") as sh_file:
            sh_file.write(script_content)
        os.chmod("run.sh", 0o755)


def main():
    # Create necessary scripts
    create_update_script()
    create_run_script() 

    print("Setup complete.")
    if is_windows():
        print("The 'update.bat' and 'run.bat' files have been created.")
        print("Run 'update.bat' to set up the environment.")
        print("Then run 'run.bat' to start the bot.")
    else:
        print("The 'update.sh' and 'run.sh' files have been created.")
        print("Run './update.sh' to set up the environment.")
        print("Then run './run.sh' to start the bot.")

if __name__ == "__main__":
    main()
