from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
import re
from typing import List
from fastapi import Depends, HTTPException
import openai

#import session
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os


# Load values from .env file into environment variables
load_dotenv()

# Retrieve values from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")
api_key = os.environ.get("OPENAI_API_KEY")

# Set up database connection
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up FastAPI app
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define the User model
Base = declarative_base()

class User(Base):
    __tablename__ = "stackaiusers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Check if table already exists
inspector = inspect(engine)
if not inspector.has_table(table_name=User.__tablename__):
    # Create table if it does not exist
    User.__table__.create(bind=engine)

# Set up Pydantic models
class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    first_name: str
    last_name: str

class UserWithEmailOut(BaseModel):
    first_name: str
    last_name: str
    email: str

# Define a class for the request body
class SummarizeRequest(BaseModel):
    data: str # The text to be summarized

# Define a class for the response body
class SummarizeResponse(BaseModel):
    summary: str # The summary of the text

class Document:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}

# Define request and response models
class GenerateAnswerRequest(BaseModel):
    question_title: str
    question_body: str
    temperature: float  # Default temperature

class GenerateAnswerResponse(BaseModel):
    answer: str

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_email(email: str):
    if not re.search(r"\.(com|edu)$", email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email must end with .com or .edu")
    if not re.search(r"@(gmail|yahoo|outlook)\.com$|@(northeastern)\.edu$", email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email must be from a supported provider (gmail.com, yahoo.com, outlook.com, or northeastern.edu)")

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one digit")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")

def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# API routes
@app.post("/signup", response_model=UserOut)
def signup(user_in: UserIn, db=Depends(get_db)):
    if not user_in.first_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="First name cannot be blank")
    if not user_in.last_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last name cannot be blank")
    validate_email(user_in.email)
    validate_password(user_in.password)
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists, please login instead")
    user = User(first_name=user_in.first_name, last_name=user_in.last_name, email=user_in.email, hashed_password=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"first_name": user.first_name, "last_name": user.last_name}

@app.post("/login", response_model=UserOut)
def login(form_data: OAuth2PasswordRequestForm=Depends(), db=Depends(get_db)):
    if not form_data.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be blank")
    if not form_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be blank")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"first_name": user.first_name, "last_name": user.last_name}

#get health
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    # Get the request parameters
    data = request.data

    # Define a prompt that guides the summarization process
    prompt = f"Summarize the following coding-related content within 300 words:\n\n{data}"

    # Initialize the OpenAI API client
    openai.api_key = api_key

    # Use the GPT-3 model to generate the summary
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose an appropriate engine
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )

    # Get the summary from the response
    summary = response.choices[0].text.strip()

    # Split the generated text into sentences by splitting at '.'
    sentences = summary.split('.')

    # Remove the last sentence if it's incomplete
    if not sentences[-1].endswith("."):
        sentences = sentences[:-1]

    # Join the sentences to create the final summary
    final_summary = ".".join(sentences)

    # Return the final summary as a response
    return SummarizeResponse(summary=final_summary)

# Define a route for generating AI answers based on user input
@app.post("/generate_answer", response_model=GenerateAnswerResponse)
def generate_answer(request: GenerateAnswerRequest):
    # Combine the user input into the "data" variable
    data = f"{request.question_title}\n{request.question_body}"
    # Initialize the OpenAI module
    openai.api_key = api_key
    # Use the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Give a solution to this programming or technology related question:"},
            {"role": "system", "content": f"Data: {data}"}
        ],
        temperature=request.temperature,
        max_tokens=500
    )

    # Extract and return the model-generated answer from the response
    answer = response["choices"][0]["message"]["content"].strip()
    return GenerateAnswerResponse(answer=answer)

@app.post("/generate_stackoverflow_question", response_model=GenerateAnswerResponse)
def generate_stackoverflow_question(request: GenerateAnswerRequest):
    # Combine the user input into the "data" variable
    data = f"{request.question_title}\n{request.question_body}"
    # Initialize the OpenAI module
    openai.api_key = api_key

    # Use the OpenAI API to generate the title
    title_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Craft a 'title' for a Stack Overflow question for this programming or software related problem :"},
            {"role": "system", "content": f"Data: {data}"}
        ],
        temperature=request.temperature,
        max_tokens=100
    )
    title = title_response["choices"][0]["message"]["content"].strip()

    # Use the OpenAI API to generate the details of the problem
    details_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Craft a 'What are the details of your problem?' section for Stack Overflow question for this programming or software related problem :"},
            {"role": "system", "content": f"Data: {data}"}
        ],
        temperature=request.temperature,
        max_tokens=300
    )
    details = details_response["choices"][0]["message"]["content"].strip()

    # Use the OpenAI API to generate what was expected from the user input
    expected_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Craft 'what were you expecting?' section for a Stack Overflow question for this programming or software related problem :"},
            {"role": "system", "content": f"Data: {data}"}
        ],
        temperature=request.temperature,
        max_tokens=100
    )
    expected = expected_response["choices"][0]["message"]["content"].strip()

    # Split the generated text into sentences by splitting at '.'
    sentences = expected.split('.')

    # Remove the last sentence if it's incomplete
    if not sentences[-1].endswith("."):
        sentences = sentences[:-1]

    # Join the sentences to create the final summary
    final_expected = ".".join(sentences)

    # Aggregate and return the generated fields as a single response
    answer = (
    f'<div style="font-size: 18px;">'
    f'<p><b style="font-size: 24px;">Question title:</b> {title}</p>'
    f'<p><b style="font-size: 24px;">Question details:</b> {details}</p>'
    f'<p><b style="font-size: 24px;">Expected solution:</b> {final_expected}</p>'
    f'</div>'
)

    return GenerateAnswerResponse(answer=answer)
