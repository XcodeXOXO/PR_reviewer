
## Please Read:
This creates a list of all packages in your venv
pip freeze > requirements.txt

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


