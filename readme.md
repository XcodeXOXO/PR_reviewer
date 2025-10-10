
## Please Read:


## This is to set the virtual Env

```bash
 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
 .venv\Scripts\activate
```

## This is to start the fastAPI Server:

```bash
 uvicorn app.main:app --reload
```

The UI runs on swagger UI managed by the fastAPI 

## Git hub commands

```bash
git add .
git commit -m " ____ "
git push origin main
```

## ngrok

This is used to tunnel localhost link to public link.
port 8000 is my port to the fast API 
127.0.0.1:8000
```bash
ngrok http 8000
```

