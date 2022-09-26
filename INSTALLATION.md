# Installation

## Without Virtual Environment

```
git clone https://github.com/WebBreacher/WhatsMyName
cd whatsmyname
pip3 install -r requirements.txt
```

You are now ready to go for your first command, example below, and see above in the **Command Line Arguments section**:

```
python whats_my_name.py -u yooper
```

or

```
python3 whats_my_name.py -u yooper
```


## With Virtual Environment

If you prefer to use a virtual environment to isolate the script:

```
mkdir myvirtualenv
cd myvirtualenv
```

example if you want to use Python 3.9:

```
python3.9 -m venv myvirtualenv
```

This command will activate your virtual environment:

```
source myvirtualenv/bin/activate
```

Once your virtual environment is activated:

```
git clone https://github.com/WebBreacher/WhatsMyName
cd whatsmyname
pip3 install -r requirements.txt
```

**Without installation of the the requirements.txt file (the Py libs), the script won't work.** 

You are now ready to go for your first command, example below, and see above in the **Command Line Arguments section**:

```
python whats_my_name.py -u yooper
```

or

```
python3 whats_my_name.py -u yooper
```

