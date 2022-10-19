import os
import json
from typing import ParamSpec
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    CORS(app)
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS"
        )
        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    def format(data):
        """
        A small utility function that calls format on each model data

        Args:
            data (iterable): A list of model data

        Returns:
            list: The formated model data
        """
        return [d.format() for d in data]
    
    
    def all_formatted_categories():
        """
        A helper function which returns a dictionary in which the keys and values are the 
        id and type the category.
        
        Args: 
            None
        
        Returns:
                A dictionary of key,pair items that represent the category id and the category type of each category.
        """
        
        categories =   format(Category.query.all())
        return {cat['id']: cat['type'] for cat in categories}
        
        
    @app.route("/categories", methods=["GET"])
    def get_categories():
        """
        Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
        
        Methods: ['GET']
        
        Request Parameters: None
            
        Returns: 
            A JSON object with keys, `categories`, that contains an object of 
            `id: category_string` key:value pairs.
            
            Sample response: {
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
        """
        
        return jsonify(
            {
                "success": True,
                "status_code": 200,
                "message": 'OK',
                "categories": all_formatted_categories()
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        """
        Fetches a paginated set of questions, a total number of questions, all categories 
        and current category string. 
        
        Methods: ['GET']
        
        Request Parameters: 
            page - Optional (default 1) representing the page number to fetch the questions from
        
        Returns: 
            An JSON object with 10 paginated questions, total questions, object including all 
                categories, and current category string
       
        Sample response: {
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
        """
        
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        all_questions = Question.query.order_by(Question.id)
        questions_on_page = all_questions[start:end]
        
        if len(questions_on_page) == 0:
            abort(404, description={"custom_message": f"No questions on page {page}"})
        
        format_questions_on_page = format(questions_on_page)
        
        categories =  all_formatted_categories()
        
        return jsonify(
            {
                "success": True,
                "status_code": 200,
                "message": 'OK',
                "questions": format_questions_on_page,
                "total_questions": all_questions.count(), 
                'categories': categories,
                'currentCategory': ''
            }
        )


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """
        Deletes a question with the specified ID. 
        
        Methods: ['DELETE']
        
        Request Arguments: 
            question_id": ID of the question to be deleted
        
        Returns: 
            A JSON object with a success key, status code, message and the ID of the deleted question. 
        
        Sample response: {
            "success": true,
            "status_code": 200,
            "message": "Question deleted",
            "question_id": 23,
        }
        """
        
                
        question = Question.query.filter(Question.id == question_id).one_or_none() 
        
        if question is None:
            abort(404, description={
                'custom_message': f"Question with `id` {question_id} does not exist"})

        try:         
            question.delete()

        except:
            abort(500, description={'custom_message': 
                f"Internal server error occurred. Question with `id` {question_id} could not be deleted"})
            
        return jsonify(
                {
                    "success": True,
                    "status_code": 200,
                    "message": "Question deleted",
                    "question_id": question_id
                }
            )

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    def validate_create_question(body):
        error_code = 400
        success = False
        error_body = '''The request body must a JSON object in the below format:  
                {
                    "question":  "<The question>",
                    "answer":  "<The answer>",
                    "difficulty": "<integer: the question difficulty >",
                    "category": "<integer: the question category>",
                }

            '''
        
        if body:
            keys = ('answer','question','category','difficulty')
            
            # A list of Booleans to check if the keys are present in the body
            check_keys = [key in body for key in keys]
            
            # If all keys and values are present
            if all(check_keys) and all(body.values()):
                try:
                    category = int(body['category'])
                    difficulty = int(body['difficulty'])
                    success = True
                except ValueError:
                    # success = False
                    error_code = 422
                    error_body = "'category' and 'difficulty' must be integers"
                    # abort(422, description={'custom_message': '"category" and "difficulty" must be integers'})         
            
            # else:
            #     # error_code = 400
            #     success = False
            #     abort(400, description={'custom_message': error})
        
        return {
            'success': success,
            'error': '' if success else error_code,
            'message': '' if success else error_body
        }
    
        
    @app.route("/questions", methods=["POST"])
    def create_question():
        """
        Creates and stores a new question into the database.
        
        Methods: ['POST']
        
        Request Parameters: None
        
        Request Data: A JSON object containing the following keys: `question`, `answer`, `category` and `difficulty`. 
            with values  of types string, string, int, and int respectively.
        
        Sample request data: {
            "question": "What club won the 2013 champions league",
            "answer": "Bayern Munich",
            "category": 6,
            "difficulty": 2
        } 
        
        Returns: A JSON object which includes a status of 201 Created and the question ID of the created question.
        Sample response: {
                "success": True,
                "status_code": 201,
                "message": "Question Created",
                "question_id": 25
            }
        """
        
        body = request.get_json()
        
        results = validate_create_question(body)
        
        if results['success']:
            # Test if that question already exist
            check_question = Question.query.filter_by(
                                    question=body['question'], answer=body['answer'], 
                                    category=body['category']
                                ).one_or_none()
            if check_question:
                abort(422, description={'custom_message': 
                f"The question already exists with an ID {check_question.id}"})
                
            
            new_question = Question(question=body['question'], answer=body['answer'], 
                                    category=body['category'], difficulty=body['difficulty'])
            try:     
                new_question.insert()
                
                # To get the id of the created question
                get_inserted_question = Question.query.filter_by(
                                    question=body['question'], answer=body['answer'], 
                                    category=body['category'], difficulty=body['difficulty']
                                ).one_or_none()
                
            except:
                abort(500, description={'custom_message': 
                f"Internal server error occurred whiles creating the question."})
                
        else:
            # When request body validation fails
            abort(results['error'], description={'custom_message': results['message']})


        return jsonify(
            {
                "success": True,
                "status_code": 201,
                "message": "Question Created",
                "question_id": get_inserted_question.id
            }
        )

        
            

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
        Searches for question(s) that match the given search term (case insensitive)
        
        Methods: ['POST']
        
        Request Parameters: None
        
        Request Data: A JSON object containing a single key `searchTerm` with the search value
        Sample request data: {
            "searchTerm": "champions"
        } 
        
        Returns: A JSON object which includes a key - `questions` - that contains list of dictionary of questions that
            match the search term or empty list if no match, total questions that matched the search term 
            and the current category.
            
        Sample response: {
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
        """
        body = request.get_json()

        # check if request body is not empty and "searchTerm" is present in the body
        if not (body and ('searchTerm' in body)):
            error_body = '''The request body must a JSON object in the below format: 
                {"searchTerm": "<your search keyword>"}
            '''
            abort(400, description={'custom_message': error_body})
        
        # description={'custom_message': error_body}

        search_term = body.get("searchTerm")
        
        try:   
            search = Question.query.filter(Question.question.ilike(f"%{search_term}%"))    

        except:
            abort(500)
            
        questions = [] # returns empty list if no searchTerm is matched
        
        if search:
            questions = format(search)
                
        return jsonify({
            'questions': questions,
            'totalQuestions': search.count(),
            'currentCategory': ''
        })
        
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_for_category(category_id):
        """
        Returns a list of all the questions available for a given category or an empty list
        when there are no questions in that category
        
        Methods: ['GET']

        Request Arguments: 
            category_id: ID of the category to fetch questions from
             
        Returns: A JSON object which includes a key - `questions` - that contains list of dictionary of questions that
            of the matched category, total questions in that category and the current category 
            and the current category.
            
        Sample response: {
            'success': True,
            'status_code': 200,
            'message': 'OK',
            'questions': [
                {
                    'id': 10,
                    'question': 'What is the heaviest organ in the human body?',
                    'answer': 'Liver',
                    'category': 1,
                    'difficulty': 4
                },
                {
                    "answer": "Blood",
                    "category": 1,
                    "difficulty": 4,
                    "id": 22,
                    "question": "Hematology is a branch of medicine involving the study of what?"
                }
            ],
            'total_questions': 2,
            'current_category': 'Science'
        }
        """

        category = Category.query.get(category_id)
        
        if not category:
            abort(404, description={'custom_message': 
                f"The category with ID {category_id} does not exist"})

        cat_questions = Question.query.filter(Question.category==category_id)
        format_cat_questions = format(cat_questions)
        
        
        return jsonify({
            'success': True,
            'status_code': 200,
            'message': 'OK',
            'questions': format_cat_questions,
            'total_questions': cat_questions.count(),
            'currentCategory': category.type
        })
     
        
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    def validate_next_question(body):
        error_code = 400
        success = True
        error_body = '''The request body must a JSON object in the below format:  
                {
                    'previous_questions':  '<List of IDs of previous questions>',
                    'quiz_category':  '<ID of the category>',
                }

            '''

        if body:
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', "")

            # if previous_questions is not an empty list 
            if previous_questions: 
                # check the data types of the previous questions if they are integers
                check_type_of_question_IDs = [isinstance(q_id, int) for q_id in previous_questions]
                
                if not (isinstance(previous_questions, list) and all(check_type_of_question_IDs)) :
                    # error_code = 422   
                    success = False         
                
            # If quiz_category was supplied
            if quiz_category:
                if not (isinstance(quiz_category, int)):
                    success = False
                 
            # If any of the validation fails 
            if not success:
                error_code = 422
                error_body = "'previous_questions' must be a list of integers and 'quiz_category' must be an integer"
                
        else:
            success = False
                
        return {
            'success': success,
            'error': '' if success else error_code,
            'message': '' if success else error_body
        }
        
            
    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        """
        Returns a random question for the quiz from the given category if given or from any category
        , that is different from any previous question in the previous questions.
        
        Methods: ['POST']
        
        Request Parameters: None
        
        Request Data: A JSON object containing the following keys - `previous_questions` and  `quiz_category`. 
            The values associated with these keys should be a list of question IDs and an integer representing the current category, respectively.
            If no previous_question or quiz category, given it returns a random question from any category.
        
        Sample request data: {
            "previous_questions": [1,22,24,12],
            "quiz_category": 1,
        } 
        
        Returns: A JSON object which includes a random question and status messages.
        
        Sample response: {
            "success": True,
            "status_code": 200,
            "message": 'OK',
            'question': {
                    'id': 5,
                    'question': "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
                    'answer': 'Maya Angelou',
                    'category': 4,
                    'difficulty': 2
                }
        }
        """
        
        body = request.get_json()
        
        results = validate_next_question(body)
        
        if results['success']:
        
            # validation has already been done we are only getting them for the query
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", "")
             
            if quiz_category:
                next_available_questions = Question.query.filter(Question.category == quiz_category,
                                                Question.id.not_in(previous_questions) ).all()
            else:
                next_available_questions = Question.query.filter(
                                                Question.id.not_in(previous_questions) ).all()    
        
            if next_available_questions:
                random.shuffle(next_available_questions) # To pick a random question
                next_question = next_available_questions[0].format()
                
            else:
                abort(404, description={'custom_message':"No more questions found"}) # If there is no more question available
        
        else:
            abort(results['error'], description={'custom_message': results['message']})

        
        return jsonify(
            {
                "success": True,
                "status_code": 200,
                "message": 'OK',
                "question": next_question
            }
        )
        
        
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": customize_error_message(error)
                     or error.name}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, 
                     "message": customize_error_message(error) or "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, 
                        "error": 400, 
                        "message": customize_error_message(error) or error.name}), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, 
                     "message": customize_error_message(error) or "method not allowed"}),
            405,
        )
        
        
    @app.errorhandler(500)
    def internal_serval_error(error):
        return jsonify({
            "error": 500,
            "message": customize_error_message(error) or error.name,
            "success": False
        })
        
        
    def customize_error_message(error):
        try:
            if error.description['custom_message']:
                message = error.description['custom_message']
                return message
        except:
            return None
        

    return app

