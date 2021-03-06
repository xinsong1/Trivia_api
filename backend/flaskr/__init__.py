import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resource={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add(
          "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
      )
      response.headers.add(
          "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
      )
      return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route("/categories")
  def retrieve_categories():
      try:
          selection = Category.query.order_by(Category.id).all()
          categories_dict = {}

          for category in selection:
              categories_dict[category.id] = category.type


          return jsonify(
              {
                  "success": True,
                  "categories": categories_dict,
                  "total_categories": len(Category.query.all()),
              }
          )
      except Exception as e:
          print(e)
          abort(500)


  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route("/questions")
  def retrieve_questions():
      selection = Question.query.order_by(Question.id).all()
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      current_questions = selection[start:end]

      if len(current_questions) == 0:
          abort(404)

      categories = Category.query.all()
      categories_dict = {category.id: category.type for category in categories}


      question_list = []
      for q in current_questions:
          question_list.append({
              'id': q.id,
              'question': q.question,
              'answer': q.answer,
              'difficulty': q.difficulty,
              'category': q.category
          })
      return jsonify(
          {
              "success": True,
              "questions": question_list,
              "total_questions": len(Question.query.all()),
              "categories": categories_dict,
              "current_category": None
          }
      )



  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):

      question = Question.query.filter(Question.id == question_id).one_or_none()


      if question is None:
          # quesiton do not exist
          abort(404)

      else:
          try:

              question.delete()
              selection = Question.query.order_by(Question.id).all()
              current_questions = paginate_questions(request, selection)

              return jsonify(
                  {
                      "success": True,
                      "deleted": question_id,
                      "questions": current_questions,
                      "total_questions": len(Question.query.all()),
                  }
              )

          except Exception as e:
              print(e)
              abort(422)
  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route("/questions", methods=["POST"])
  def create_question():
      body = request.get_json()

      new_question = body.get("question", None)
      new_answer = body.get("answer", None)
      new_difficulty = body.get("difficulty", None)
      new_category = body.get("category", None)


      try:

          question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
          question.insert()

          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify(
              {
                  "success": True,
                  "created": question.id,
                  "questions": current_questions,
                  "total_questions": len(Question.query.all()),
              }
          )

      except:
          abort(422)
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route("/search", methods=["POST"])
  def search_question():
      body = request.get_json()

      search = body.get("search", None)
      # print(search)

      try:

          selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))

          current_questions = paginate_questions(request, selection)

          return jsonify({
                  "success": True,
                  "questions": current_questions,
                  "total_questions": len(selection.all())
                  })


      except:
          abort(422)



  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:category_id>/questions')
  def show_questions_by_category(category_id):
      selection = Question.query.filter_by(category=str(category_id)).all()
      # print(selection)

      if len(selection) == 0:
          abort(404)

      question_list = []
      for q in selection:
          question_list.append({
              'id': q.id,
              'question': q.question,
              'answer': q.answer,
              'difficulty': q.difficulty,
              'category': q.category
          })

      return jsonify({
          'success': True,
          'questions': question_list,
          'total_questions': len(selection),
          'category': Category.query.get(category_id).format()
      })

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      body = request.get_json()
      previous_questions = body.get('previous_questions', None)
      selected_category = body.get('quiz_category', None)
      print(selected_category)


      if selected_category['id'] == 0:
          unused_questions = Question.query.order_by(Question.id).filter(Question.id.notin_(previous_questions)).all()
      else:
          category_id = selected_category['id']
          unused_questions = Question.query.order_by(Question.id).filter(Question.category==category_id,Question.id.notin_(previous_questions)).all()
      print(unused_questions)
      if len(unused_questions) > 0:
          # print(len(unused_questions))
          index = random.randint(0, len(unused_questions)-1)
          # print(index)
          new_question = unused_questions[index].format()
          return jsonify(
          {
            'question': new_question
          }
          )
      else:
          abort(405)





  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
      return (
          jsonify({"success": False, "error": 404, "message": "resource not found"}),
          404,
      )

  @app.errorhandler(422)
  def unprocessable(error):
      return (
          jsonify({"success": False, "error": 422, "message": "unprocessable"}),
          422,
      )

  @app.errorhandler(400)
  def bad_request(error):
      return (
          jsonify({"success": False, "error": 400, "message": "bad request"}),
          400,
      )

  @app.errorhandler(405)
  def not_allowed(error):
      return (
          jsonify({"success": False, "error": 405, "message": "method not allowed"}),
          405,
      )
  @app.errorhandler(500)
  def server_error(error):
      return (
          jsonify({"success": False, "error": 500, "message": "initeral server error"}),
          500,
      )

  return app
