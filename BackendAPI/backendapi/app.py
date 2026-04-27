from fastapi import FastAPI

from backendapi.routers import token, user

app = FastAPI(title='API Sitema Bancário')


app.include_router(user.router)
app.include_router(token.router)


@app.get('/')
def read_root():
    return {'msg': 'teste'}
