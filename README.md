# README

# Setup

First, [Get Python 3](https://www.python.org/downloads/) and install.

Then, download the [virtualenv](https://virtualenv.pypa.io/en/latest/)
package

```
$ pip install virtualenv
```

Because everyone's installed pip packages will be different, I like using virtual environment to make sure only the ones that are needed are installed.

In the cloned project folder type:
```
$ virtualenv venv
```
This creates virtual environment files in `/venv`

Then type
```
$ venv/scripts/activate
```
If the above doesn't work, try:
```
$ . venv/scripts/activate
```
If it works, you should see `(venv)` at the beginning of the next line. This means your virtual environment is activated and any packages you install are confined in it.

# Installing dependencies

After you're inside a virtual environment:
```
$ pip install -r requirements.txt
```
This will install all the dependencies inside the `requirements.txt`

# Execution

Simply run
```
$ python main.py
```
I've moved some settings into the file `settings.py`, this is just for separation of concerns. There will likely more things added to settings.py if this thing requires more flexibility (such as number of threads, etc)
