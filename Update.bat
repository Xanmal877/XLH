REM Create a virtual environment named XLHenv
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the required packages from piplist.txt
pip install wheel
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r piplist.txt

REM Create or empty the .env file
type nul > .env

REM Create directories
mkdir WavFiles
mkdir WavFiles\Output
mkdir DownloadedMedia

REM Notify the user
echo Setup complete.
pause
