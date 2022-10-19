import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.username = "student"
        self.password = "student"
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.username, self.password, "localhost:5432", self.database_name
        )
        
        ran_num = random.randint(1,1000)
        self.test_question = {
            "question": f"Create test question {ran_num}",
            "answer": f"test answer {ran_num}",
            "category": random.randint(1, Category.query.count()),
            "difficulty": random.randint(1,6)
        }
        
        
        setup_db(self.app, self.database_path)
        # setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
            
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """A request to get all the categories"""

        response = self.client().get("/categories")
        response_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], 'OK')
        self.assertTrue(response_data['success'])
        self.assertIsInstance(response_data['categories'], dict)
        
          
    def test_success_get_questions(self):
        """A request to get paginated questions"""

        response = self.client().get("/questions")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], 'OK')
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['total_questions'])
        self.assertIsInstance(response_data['total_questions'], int)
        self.assertIsInstance(response_data['questions'], list)
        self.assertIsInstance(response_data['questions'][0], dict)
        self.assertIsInstance(response_data['categories'], dict)
        
        if response_data['total_questions'] > 10:
            # questions returned should be 10 or less depending on the page
            self.assertLessEqual(len(response_data['questions']), 10) 
        
        
    def test_404_get_questions_on_invalid_page(self):
        '''Return error if no questions on page provided'''
        
        response = self.client().get('/questions?page=1000000')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['error'], 404)
        self.assertEqual(response_data['message'], 'No questions on page 1000000')
        
        
    def test_delete_question_success(self):
        """Delete a question from the database given the ID of the question"""
        
        # Create a new question and insert into the database
        response_create_question = self.client().post("/questions", json=self.test_question)
        response_create_question_data = json.loads(response_create_question.data)
        # Get the ID of the newly created test question
        # print(f"{response_create_question_data=}")
        question_id = response_create_question_data['question_id']

        response_delete_question = self.client().delete(f'/questions/{question_id}')
        response_delete_question_data = json.loads(response_delete_question.data)

        self.assertEqual(response_delete_question.status_code, 200)
        self.assertTrue(response_delete_question_data['success'])
        self.assertEqual(response_delete_question_data['message'], "Question deleted")
        self.assertEqual(response_delete_question_data['question_id'], question_id)


    def test_delete_question_non_existent_404(self):
        """Deleting a question with a non-existent id should return a 404 error status code"""
        question_id = 1000000000000
        response = self.client().delete(f"/questions/{question_id}")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], f"Question with `id` {question_id} does not exist")
        
        
    def test_create_new_question_success(self):
        """Test to create a new question"""
        
        # Random integers used to prevent duplicate questions when the test is run again
        
        
        response = self.client().post("/questions", json=self.test_question)
        response_data = json.loads(response.data)

        # print(f"{response_data=}")
        self.assertEqual(response_data['status_code'], 201)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], "Question Created")
        self.assertIn("question_id", response_data)
        
        
    def test_create_new_question_fails_422_using_existing_question(self):
        """Test to create a new question fails with an existing question"""
        
        # Get an existing question from the db
        question = Question.query.first()
        
        
        response = self.client().post("/questions", json=question.format())
        response_data = json.loads(response.data)

        # print(f"{response_data=}")
        self.assertEqual(response_data['error'], 422)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 
                         f"The question already exists with an ID {question.id}")
        
       
       
    def test_create_new_question_fails_400_with_no_or_empty_body(self):
        """Test to create a new question fails with an existing question"""
        
        error_body = '''The request body must a JSON object in the below format:  
                {
                    "question":  "<The question>",
                    "answer":  "<The answer>",
                    "difficulty": "<integer: the question difficulty >",
                    "category": "<integer: the question category>",
                }

            '''
        
        # Case 1: No body
        response_1 = self.client().post("/questions")
        response_data_1 = json.loads(response_1.data)

        # print(f"{response_data=}")
        self.assertEqual(response_data_1['error'], 400)
        self.assertFalse(response_data_1['success'])
        
        # Case 2: Empty body  
            
        response = self.client().post("/questions", json={})
        response_data = json.loads(response.data)

        # print(f"{response_data=}")
        self.assertEqual(response_data['error'], 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
        
    
    
    def test_get_questions_by_category_success(self):
        """Get questions by category"""
        
        random_category_id = random.randint(1,6)
        random_category = Category.query.get(random_category_id)
        response = self.client().get(f'/categories/{random_category.id}/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertIsInstance(response_data['total_questions'], int)
        self.assertIsInstance(response_data['questions'][0], dict)
        self.assertIsInstance(response_data['questions'], list)
        self.assertTrue(response_data['currentCategory'], random_category.type )
        
    
    def test_get_questions_based_on_category_404_on_nonexistent_category(self):
        """Get questions from a category that does not exist should return a 404 error"""

        category_id = 1000000000
        endpoint = f"/categories/{category_id}/questions"

        response = self.client().get(f"/categories/{category_id}/questions")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['error'], 404)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], f"The category with ID {category_id} does not exist")
    
    
    def test_success_get_questions_based_on_search_term(self):
        """Get all questions based on a search term(case-insensitive)"""
        
        questions = Question.query.all()
        random_question = questions[random.randint(0,len(questions)-1)]
        # Get the first non-whitespace string from the question
        string_from_question = random_question.question.strip().split()[0] 
        
        body = {
            "searchTerm": string_from_question
        }
        
        response = self.client().post(f"/questions/search", json=body)
        response_data = json.loads(response.data)
              
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_data['questions']), 0)
        self.assertIsInstance(response_data['questions'], list)
        self.assertIsInstance(response_data['questions'][0], dict)
        # Check all the returned questions to see if they contain the searchTerm
 
        for question in response_data['questions']:
            self.assertIn(string_from_question.lower(), question['question'].lower())
        # self.assertIsNotNone()
        
       
    def test_400_search_questions_body_missing_or_search_term_key_not_in_body(self):
        """Throws 400 when the post body is not given or the `serachterm` key not in json body"""
        
        questions = Question.query.all()
        random_question = questions[random.randint(0, len(questions)-1)]
        # Get the first non-whitespace string from the question
        string_from_question = random_question.question.strip().split()[0] 
        
        body = {
            "Non_existent_key": string_from_question
        }
        
        error_body = '''The request body must a JSON object in the below format: 
                {"searchTerm": "<your search keyword>"}
            '''
        
        # case 1: body missing
        
        response_1 = self.client().post(f"/questions/search")
        response_data_1 = json.loads(response_1.data)
        # print(f"{response_data_1=}")
        self.assertEqual(response_1.status_code, 400)
        self.assertFalse(response_data_1['success'])
        
        # case 2: `searchterm` not in body
        response = self.client().post(f"/questions/search", json=body)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
                

    def test_success_get_next_question_for_quiz(self):
        """Get next question in the quiz. Returns a random new question not in the list ofprevious questions, 
        within the given category if given or from any category"""
        
        
        # CASE 1: Both previous_questions and category given
        
        # get a random category for the list of categories within the database
        categories = Category.query.all()
        
        random_category = categories[random.randint(0,len(categories)-1)]
        # Get the first non-whitespace string from the question
        random_category_id = random_category.id
        
        questions_in_random_category = Question.query.filter_by(category=random_category_id).all()
        
        # selecting all questions except the last 2 as previous questions
        previous_questions = [question.id for question in questions_in_random_category[:-2]]
        
        
        body = {
            "previous_questions": previous_questions,
            "quiz_category": random_category_id,
        } 
        
        response = self.client().post("/quizzes", json=body)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'OK')
        self.assertIsInstance(response_data['question'], dict)
        self.assertEqual(response_data['question']['category'], random_category_id) # to make sure the question belongs to that category

        # make sure the returned question is different from the list of previous questions
        for id in previous_questions:
            self.assertNotEqual(response_data['question']['category'], id)
            
            
        
        # CASE 2: Previous questions is an empty list and category given
        
        body = {
            "previous_questions": [],
            "quiz_category": random_category_id,
        } 
        
        response = self.client().post("/quizzes", json=body)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'OK')
        self.assertIsInstance(response_data['question'], dict)
        self.assertEqual(response_data['question']['category'], random_category_id) # to make sure the question belongs to that category

    
        # CASE 3: Previous questions is an empty list and category is empty
        # NOTE:  If quiz_category is an empty string, the next question can come from any category
        # But if is quiz_catgory is a not-empty string, validation fails.
        # The API was designed to accept only integer or empty-string for quiz_category
        
        body = {
            "previous_questions": [],
            "quiz_category": "",
        } 
        
        response = self.client().post("/quizzes", json=body)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'OK')
        self.assertIsInstance(response_data['question'], dict)
        
        self.assertIn("question", response_data['question'])
        self.assertIn("answer", response_data['question'])
        self.assertIn("category", response_data['question'])
        self.assertIn("difficulty", response_data['question'])
        
        
        # CASE 4: Previous questions is not empty but category is empty
        # NOTE: The API was designed in such a way that one of the keys can be missing but not both (in which case it throws a 400 error)
        # If previous_questions is missing, it defaults to []
        # If quiz_category is missing, it defaults to "" which means any category
        
        body = {
            "previous_questions": previous_questions,
        } 
        
        response = self.client().post("/quizzes", json=body)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'OK')
        self.assertIsInstance(response_data['question'], dict)

        # make sure the returned question is different from the list of previous questions
        for id in previous_questions:
            self.assertNotEqual(response_data['question']['category'], id)

    
    
    def test_422_get_next_question_for_quiz_if_validation_fails(self):
        """Test returns 422 error code with custom message if `quiz_category` is not an integer or `previous_questions` 
        is not a list of integers"""
        
        error_body = "'previous_questions' must be a list of integers and 'quiz_category' must be an integer"
        
        # case 1: quiz category not an integer
        body_1 = {
            "previous_questions": [1, 2, 3, 4],
            "quiz_category": "strh",
        } 
        
        response = self.client().post("/quizzes", json=body_1)
        response_data = json.loads(response.data)
        
        # print(f"{response.status_code=}")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
        
        
        # case 2: previous_questions is not a list
        body_2 = {
            "previous_questions": "1, 2, 3, 4",
            "quiz_category": 1,
        } 
        
        response = self.client().post("/quizzes", json=body_2)
        response_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
        
        # case 3: previous_questions list contain a non-integer member
        body_3 = {
            "previous_questions": [1, 2, 3, "sth"],
            "quiz_category": 1,
        } 
        
        response = self.client().post("/quizzes", json=body_3)
        response_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
        
        
        
    def test_400_get_next_question_for_quiz_if_request_body_missing_or_empty(self):
        """Test returns 400 error code with custom message if the request body is not given"""
        
        error_body = '''The request body must a JSON object in the below format:  
                {
                    'previous_questions':  '<List of IDs of previous questions>',
                    'quiz_category':  '<ID of the category>',
                }

            '''

        # CASE 1: No body at all
        response = self.client().post("/quizzes")
        response_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response_data['success'])
        
        
        # CASE 2: Body empty
        response = self.client().post("/quizzes", json={})
        response_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], error_body)
        
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()