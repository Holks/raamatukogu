set FLASK_APP=raamatukogu.py
cd %userprofile%\git\raamatukogu\Raamatukogu
call venv\scripts\activate

python -m flask run --host=0.0.0.0

