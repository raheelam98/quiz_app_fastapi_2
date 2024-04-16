
from quiz_backend.setting import access_expiry_time, refresh_expiry_time
from quiz_backend.models.user_models import User, UserModel, Token, LoginModel
from quiz_backend.controllers.auth_controllers import  (verifyPassword, passswordIntoHash, 
                                                         generateAccessAndRefreshToken,  decodeToken) # generateToken
from quiz_backend.utils.exception import (ConflictException, NotFoundException, InvalidInputException)
from quiz_backend.db.db_connector import get_session

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, select


# Expiry things 

auth_schema = OAuth2PasswordBearer(tokenUrl="")
# check :- comes with bearer-token and 

# sign_in :- need user name, email and password 
# sign_in :- email and password both or any one exist choice another email or password
# login_in :-

def signUpFn(user_form: UserModel, session: Annotated[Session, Depends(get_session)] ):
    users = session.exec(select(User))

# authenticate, email and password is already exist in Database   
    for user in users:
        is_email_exist = user.user_email == user_form.user_email
        is_password_exit = verifyPassword(
            user.user_password, user_form.user_password
        )
        if is_email_exist and is_password_exit:
            raise ConflictException("email and password")
        if is_email_exist:
            raise ConflictException("email")
        if is_password_exit:
            raise ConflictException("password")

    hashed_password = passswordIntoHash(user_form.user_password) 

    user = User(user_name=user_form.user_name,
                user_email=user_form.user_email,
                user_password=hashed_password)   

    session.add(user)   
    session.commit()
    session.refresh(user)

    # generate access-token and refresh-token
    data = {
        "user_name" : user.user_name,
        "user_email": user.user_email,
        #"user_password": user.user_email,
        "access_expiry_time" : access_expiry_time,
        "refresh_expiry_time" : refresh_expiry_time
    }
    
    # destructure
    #access_token, refresh_token = generateAccessAndRefreshToken(data)

    token_data = generateAccessAndRefreshToken(data)
    
    # Save the refresh token in the database
    #token = Token(refresh_token=token_data["refresh_token"])

    # error 1 
    # save refresh token in database
    token = Token(user_id=user.user_id, refresh_token= token_data["refresh_token"]["token"])
    
    session.add(token)
    session.commit()
    return token_data

# login controller (to fill the form require email and password)

# #def loginFn(login_form : OAuth2PasswordRequestForm, session: Annotated[Session, Depends(get_session)]):

# error :-  OAuth2PasswordRequestForm
#def loginFn(login_form: OAuth2PasswordRequestForm, session: DBSession):


def loginFn(login_form : LoginModel, session: Annotated[Session, Depends(get_session)]):
    """
    Function to log in a user.
    Args:
        login_form (OAuth2PasswordRequestForm): The login form data.
        session (Session): The database session.
    Returns:
        dict: A dictionary containing access and refresh tokens.
    """
    users = session.exec(select(User))
    for user in users:
        user_email = user.user_email
        verify_password = verifyPassword(
            user.user_password, login_form.user_password)
        
        # Check if provided credentials are valid
        ##if user_email == login_form.username and verify_password:

        # error : slove useremail (not :- login_form.username )
        if user_email == login_form.user_email and verify_password:
    
            data = {
                "user_name": user.user_name,
                "user_email": user.user_email,
                "access_expiry_time": access_expiry_time,
                "refresh_expiry_time": refresh_expiry_time
            }
            token_data = generateAccessAndRefreshToken(data)

            # Save the refresh token in the database
            #token = Token(refresh_token=token_data["refresh_token"][token])

            # Update the refresh token in the database 
            token = session.exec(select(Token).where(Token.user_id == user.user_id)).one()
            token.refresh_token = token_data["refresh_token"]["token"]

            session.add(token)
            session.commit()
            session.refresh(token)
            return token_data
    else:
        raise InvalidInputException("Email or Password")



def getUserFn(token: Annotated[str, Depends(auth_schema)], session: Annotated[Session, Depends(get_session)] ):
    """
    Function to get user details using an access token.
    Args:
        token (str): The access token.
        session (Session): The database session.
    Returns:
        User: The user object.
    """
    try:
        if token:
            # Decode the access token to get user data
            data = decodeToken(token)
            user_email = data["user_email"]
            user = session.exec(select(User).where(
                User.user_email == user_email)).one()
            return user
    except:
        raise NotFoundException("Token")
         
# through jwt decode token
# one() : only return one thing if get more or nothing it give error ???
# first() :- give the only first value but doesn't give error ???

#######  ============================================
    
DBSession = Annotated[Session, Depends(get_session)]
def signUpFn2(user_form: UserModel, session: DBSession):
    """
    Function to sign up a new user.
    Args:
        user_form (UserModel): The user details provided during sign up.
        session (Session): The database session.
    Returns:
        dict: A dictionary containing access and refresh tokens.
    """
    # Check if user already exists
    users = session.exec(select(User))
    for user in users:
        is_email_exist = user.user_email == user_form.user_email
        is_password_exist = verifyPassword(
            user.user_password, user_form.user_password)

        if is_email_exist and is_password_exist:
            raise ConflictException("email and password")
        elif is_email_exist:
            raise ConflictException("email")
        elif is_password_exist:
            raise ConflictException("password")

    # Hash the user's password
    hashed_password = passswordIntoHash(user_form.user_password)
    # Create a new user
    user = User(user_name=user_form.user_name,
                user_email=user_form.user_email, 
                user_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate access and refresh tokens for the new user
    data = {
        "user_name": user.user_name,
        "user_email": user.user_email,
        "access_expiry_time": access_expiry_time,
        "refresh_expiry_time": refresh_expiry_time
    }
    token_data = generateAccessAndRefreshToken(data)

    # Save the refresh token in the database
    #token = Token(refresh_token=token_data["refresh_token"])

    # error 
    # save refresh token in database
    token = Token(user_id=user.user_id, 
                  refresh_token= token_data["refresh_token"]["token"])
    session.add(token)
    session.commit()

    return token_data

# error 1 :-  OAuth2PasswordRequestForm
#def loginFn2(login_form: OAuth2PasswordRequestForm, session: DBSession):

def loginFn2(login_form: LoginModel, session: DBSession):
    """
    Function to log in a user.
    Args:
        login_form (OAuth2PasswordRequestForm): The login form data.
        session (Session): The database session.
    Returns:
        dict: A dictionary containing access and refresh tokens.
    """
    users = session.exec(select(User))
    for user in users:
        user_email = user.user_email
        verify_password = verifyPassword(
            user.user_password, login_form.user_password)
        # error : login_form.user_password  (not :- login_form.password)
        
        # Check if provided credentials are valid
        if user_email == login_form.user_email and verify_password:
            data = {
                "user_name": user.user_name,
                "user_email": user.user_email,
                "access_expiry_time": access_expiry_time,
                "refresh_expiry_time": refresh_expiry_time
            }
            token_data = generateAccessAndRefreshToken(data)

            # error 2
            # Save the refresh token in the database
            #token = Token(refresh_token=token_data["refresh_token"])
            
            # Update the refresh token in the database 
            token = session.exec(select(Token).where(Token.user_id == user.user_id)).one()
            token.refresh_token = token_data["refresh_token"]["token"]

            session.add(token)
            session.commit()
            session.refresh(token)
            return token_data
    else:
        raise InvalidInputException("Email or Password")



    
#######  ============================================    
    
# get-user (base on token) auth provide all related things of token (use bearer token) 
# def getUsersFn(token: Annotated[str, Depends(auth_schema)], session: Annotated[Session, Depends(get_session)]):
#     """
#     Function to get user details using an access token.
#     Args:
#         token (str): The access token.
#         session (Session): The database session.
#     Returns:
#         User: The user object.
#     """
#     try:
#         if token:
#             data = decodeToken(token)

#             # dict.keys() :- returns a list of all the available keys in the dictionary
#             user_email = data["user_email"]
#             # select user structure
#             user = session.exec(select(User).where(User.user_email == user_email)).one()
#             return user
#     except :
#         raise NotFoundException("Token")    