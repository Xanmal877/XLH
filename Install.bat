@echo off

REM Check if XLH environment exists
if exist XLH\Scripts\activate (
    echo "XLH environment already exists."
    call XLH\Scripts\activate

    REM Install the required packages from piplist.txt
    if exist piplist.txt (
        pip install -r piplist.txt

        pause
    ) else (
        echo "piplist.txt not found."
        pause
    )

    REM Deactivate the virtual environment
    deactivate
) else (
    REM Create and activate the virtual environment if it doesn't exist
    python -m venv XLH
    if "%errorlevel%"=="0" (
        call XLH\Scripts\activate

        REM Install the required packages from piplist.txt
        if exist piplist.txt (
            pip install -r piplist.txt
            pause
        ) else (
            echo "piplist.txt not found."
            pause
        )

        REM Deactivate the virtual environment
        deactivate
    ) else (
        echo "Failed to create virtual environment."
        pause
    )
)
