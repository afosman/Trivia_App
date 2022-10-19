# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

<!-- ## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500. -->

#### API Documention

### API Endpoints

  - GET '/categories'
  - GET '/questions?page=${integer}'
  - DELETE '/questions/${id}'
  - POST '/questions'
  - POST '/questions/search'
  - GET '/categories/${id}/questions'
  - POST '/quizzes'


## `GET '/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the       corresponding string of the category
        
- Methods: ['GET']

- Request Parameters: None
    
- Returns: 
    A JSON object with keys, `categories`, that contains an object of 
    `id: category_string` key:value pairs.
    
    Sample response: 
    {
      "success": true,
      "status_code": 200,
      "message": 'OK',
      "categories": { 
          '1' : "Science",
          '2' : "Art",
          '3' : "Geography",
          '4' : "History",
          '5' : "Entertainment",
          '6' : "Sports" 
      }
    }


## `GET '/questions?page=${integer}'`

- Fetches a paginated set of questions, a total number of questions, all categories 
        and current category string. 
        
- Methods: ['GET']

- Request Parameters: 
    page - Optional (default 1) representing the page number to fetch the questions from

- Returns: 
    An JSON object with 10 paginated questions, total questions, object including all 
        categories, and current category string

    Sample response: 
    {
      "success": true,
      "status_code": 200,
      "message": 'OK',
      "questions": [
          {
            "answer": "Lake Victoria",
            "category": 3,
            "difficulty": 2,
            "id": 13,
            "question": "What is the largest lake in Africa?"
          },
          {
            "answer": "The Palace of Versailles",
            "category": 3,
            "difficulty": 3,
            "id": 14,
            "question": "In which royal palace would you find the Hall of Mirrors?"
          }
        ],
        "total_questions": 2,
        "categories": {
            '1' : "Science",
            '2' : "Art",
            '3' : "Geography",
            '4' : "History",
            '5' : "Entertainment",
            '6' : "Sports"
        },
        "current_category": ""
    }


## `DELETE '/questions/${id}'`

- Deletes a question with the specified ID. 
        
- Methods: ['DELETE']

- Request Arguments: 
    question_id": ID of the question to be deleted

- Returns: 
    A JSON object with a success key, status code, message and the ID of the deleted question. 

  Sample response: 
  {
    "success": true,
    "status_code": 200,
    "message": "Question deleted",
    "question_id": 23
  }


## `POST '/questions'`

- Creates and stores a new question into the database.
        
- Methods: ['POST']

- Request Parameters: None

- Request Data: A JSON object containing the following keys: `question`, `answer`, `category` and   `difficulty` with values  of types string, string, int, and int respectively.

  Sample request data: 
  {
    "question": "What club won the 2013 champions league",
    "answer": "Bayern Munich",
    "category": 6,
    "difficulty": 2
  } 

- Returns: A JSON object which includes a status of 201 Created and the question ID of the created question.

    Sample response: 
    {
        "success": True,
        "status_code": 201,
        "message": "Question Created",
        "question_id": 25
      }


## `POST '/questions/search'`

- Searches for question(s) that match the given search term (case insensitive)
        
- Methods: ['POST']

- Request Parameters: None

- Request Data: A JSON object containing a single key `searchTerm` with the search value
    Sample request data: 
    {
        "searchTerm": "champions"
    } 

- Returns: A JSON object which includes a key - `questions` - that contains list of dictionary of questions that match the search term or empty list if no match, total questions that matched the search term and the current category.
    
  Sample response: 
  {
    'success': True,
    'questions': [
        {
          "answer": "Edward Scissorhands",
          "category": 5,
          "difficulty": 3,
          "id": 6,
          "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        },
        {
          "answer": "Uruguay",
          "category": 6,
          "difficulty": 4,
          "id": 11,
          "question": "Which country won the first ever soccer World Cup in 1930?"
        },
        {
          "answer": "George Washington Carver",
          "category": 4,
          "difficulty": 2,
          "id": 12,
          "question": "Who invented Peanut Butter?"
        },

    ],
    'current_category': '',
    'total_questions': 3
  }


## `GET '/categories/${id}/questions'`

- Returns a list of all the questions available for a given category.
        
- Methods: ['GET']

- Request Arguments: 
    category_id: ID of the category to fetch questions from
      
- Returns: A JSON object which includes a key - `questions` - that contains list of dictionary of questions that of the matched category, total questions in that category and the current category and the current category.
    
  Sample response: 
  {
    "success": True,
    "status_code": 200,
    "message": "OK",
    "questions": [
      {
        "id": 10,
        "question": "What is the heaviest organ in the human body?",
        "answer": "Liver",
        "category": 1,
        "difficulty": 4
      },
      {
        "answer": "Blood",
        "category": 1,
        "difficulty": 4,
        "id": 22,
        "question": "Hematology is a branch of medicine involving the study of what?"
      }
    ],
    "total_questions": 2,
    "current_category": "Science"
  }


## `POST '/quizzes'`

- Returns a random question for the quiz from the given category if given or from any category that
, that is different from any previous question.

- Methods: ['POST']

- Request Parameters: None

- Request Data: A JSON object containing the following keys - `previous_questions` and  `quiz_category`. 
    The values associated with these keys should be a list of question IDs and an integer representing the current category, respectively.
    If no quiz category is given, it returns a random question from any category.

  Sample request data: 
  {
    "previous_questions": [1,22,24,12],
    "quiz_category": 1,
  } 

- Returns: A JSON object which includes a random question and status messages.

  Sample response: 
  {
    "success": True,
    "status_code": 200,
    "message": 'OK',
    "question": {
      'id': 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": 'Maya Angelou',
      "category": 4,
      "difficulty": 2
    }
  }


## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
