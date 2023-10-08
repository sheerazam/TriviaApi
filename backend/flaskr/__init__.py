from crypt import methods
import os
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
  
  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @DONE 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })

  '''
  DONE
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.order_by(Question.id).all()
    total_questions = len(questions)
    if len(questions) == 0:
      abort(404)
    categories = Category.query.order_by(Category.id).all()
    categoriesFormated = [category.format() for category in categories]

    categories_returned = []
    for cat in categoriesFormated:
      categories_returned.append(cat['type'])

    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions[start:end]],
      'total_questions': total_questions,
      'categories': categories_returned ,
      'current_category': categories_returned
    })
  '''
  @DONE
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)
    question.delete()
    return jsonify({
      'success': True,
      'deleted': question_id
    })

  '''
  DONE
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  DONE
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    searchTerm = body.get('searchTerm', None)
    if(searchTerm is not None):
      questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
      if len(questions) == 0:
        abort(404, {'message': 'No questions found'})
      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': None
      })
    else:
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = body.get('category', None)
      if len(new_question) == 0 or len(new_answer) == 0 or len(new_difficulty) == 0 or len(new_category) == 0:
        abort(400, {'message': 'Question, Answer, Category or Difficulty can not be blank'})
      try:
        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
        question.insert()
        return jsonify({
          'success': True,
          'created': question.id
      })
      except:
        abort(422)


  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<string:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    if len(questions) == 0:
      abort(404, {'message': 'No questions found for this category'})
    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions],
      'total_questions': len(questions),
      'current_category': category_id
    })

  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    if quiz_category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter(Question.category == str(int(quiz_category['id']) - 1)).all()
    if len(questions) == 0:
      abort(404, {'message': 'No questions found for this category'})
    random_question = random.choice(questions)
    while random_question.id in previous_questions:
      random_question = random.choice(questions)
    return jsonify({
      'success': True,
      'question': random_question.format()
    })

  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal Server Error"
    }), 500

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Method not allowed"
    }), 405

  
  return app

    