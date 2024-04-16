from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from contextlib import asynccontextmanager
from typing import Annotated

from quiz_backend.db.db_connector import  createTable  #, get_session
from quiz_backend.models.user_models import User
from quiz_backend.utils.exception import (NotFoundException, InvalidInputException, ConflictException)
from quiz_backend.controllers.user_controllers import signUpFn, loginFn 

from quiz_backend.controllers.user_controllers import signUpFn2 , loginFn2 

#from quiz_backend.controllers.user_controllers import getUserFn

# define async context manager for appliction lifespan
@asynccontextmanager
async def life_span(app: FastAPI):
    print("Creating tables ... ")
    createTable()
    yield
    
# create FastAPI application instance with custom lifespan event handler
app = FastAPI(lifespan=life_span)

## FastAPI provide exception_handlers :- @app.exception_handler()
@app.exception_handler(NotFoundException)
def not_found(request: Request, exception: NotFoundException):
    return JSONResponse(status_code=404, content=f"{exception.not_found} Not Found ... " )

@app.exception_handler(InvalidInputException)
def invalid_input(request: Request, exception: InvalidInputException):
    return JSONResponse(status_code=422, content=f'invalid {exception.invalid_input} ... ' )
    
@app.exception_handler(ConflictException) 
def conflict_input(request: Request, exception: InvalidInputException):
    return JSONResponse(status_code=400, content=f'{exception.conflict_input} already exit ...')   

# define route for home endpoint
@app.get("/")
def home():
    return "Quiz Project"

# # query parameter (?)
# def getUser(name : str):
#     return name

# @app.get("/api/getUser")
# def get_user(user: Annotated [str,Depends(getUser)]):
#     return user

# @app.get("/api/user")
# def postLogin(user):
#     return user

@app.post("/api/userSignup")
def user_signup(token_data: Annotated[dict, Depends(signUpFn)]):
    if not token_data:
        raise NotFoundException("User")
    return token_data

@app.post("/api/userSignin")
def user_sigin(token_data: Annotated[dict, Depends(loginFn)]):
    if not token_data:
        raise NotFoundException("User")
    return token_data

# @app.get("/api/getUsers")
# def get_users(token_data: Annotated[dict, Depends(getUserFn)]):
#     if not token_data:
#         raise NotFoundException("User")
#     return token_data 

#######  ============================================    

@app.post("/api/userSignup2")
def user_signup2(token_data: Annotated[dict, Depends(signUpFn2)]):
    if not token_data:
        raise NotFoundException("User")
    return token_data

@app.post("/api/userSignin2")
def user_sigin2(token_data: Annotated[dict, Depends(loginFn2)]):
    if not token_data:
        raise NotFoundException("User")
    return token_data