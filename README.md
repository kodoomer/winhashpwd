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
* **the folder contents should look the following**
  * `main.py`
  * `lsa.txt`
  * `psexec.exe`
* run `python -m pip install pycryptodomex`
* run `python main.py` \
*tested on my windows 11 machine with a local account*
  
---

the hash has to be a MD4 hash of a UTF-16-LE encoded password string \
this program **only works with the password and NOT the pin**
#### beware 
there are no checks in the program to make sure you dont mess anything up!

---
most of the information about how windows stores passwords has been taken from [endermanch](https://github.com/Endermanch) and [his script](https://github.com/Endermanch/scripts/blob/main/sam/samviewer.py) \
**none of the code was used**
