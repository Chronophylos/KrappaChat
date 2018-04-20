build:
    pipenv run pyinstaller --windowed --strip --onefile --name krappachat krappachat/__main__.py

test:
    pipenv check
    pipenv run pycodestyle krappachat
    pipenv run pydocstyle krappachat
