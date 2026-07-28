a little project that allows you to view and modify the password hash of a windows user

#### how to use
do all the following in the project directory:
* [download psexec (or psexec64)](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec) and rename it to psexec.exe
* run command prompt as administrator
* run `psexec.exe -s -i regedit.exe`
* in the registry editor go to `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa`
* press `CTRL+P`, select "Microsoft Print to PDF" and save to a file
* create a file `lsa.txt` and copy all the text from the pdf file to it
* delete the pdf file and close the registry editor
* run `python -m pip install pycryptodomex`
* run `python main.py`
---
the hash has to be a MD4 hash of a UTF-16-LE encoded password string
#### beware 
there are no checks in the program to make sure you dont mess anything up!
