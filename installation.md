# WhatsMyName Python Script installation 
If you prefer to use a virtual environment to isolate the script:

```
mkdir myvirtualenv
```

```
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
```

```
cd WhatsMyName
```

```
pip3 install -r requirements.txt
```

**Without installation of the the requirements.txt file (Py libs), the script won't work.** 

You are now ready to go for your first command using the WMN script.

<br>

Example below, and see also: [**Command Line Arguments**](https://github.com/WebBreacher/WhatsMyName#command-line-arguments)

```
python whats_my_name.py -u yooper --format table
```

or

```
python3 whats_my_name.py -u yooper --format table
```
