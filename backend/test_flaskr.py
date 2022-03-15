import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
          "question": "How old is the Earth Planet?",
          "answer": "4.5 billion years",
          "category": "1",
          "difficulty": 2
        }
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories():
        res = self.client.get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], Ture)
        self.assertTure(len(data['categories']))


    def test_get_paginated_questions(self):
        res = self.client().get("/api/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/api/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/api/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/api/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_search_question(self):
        res = self.client().get('/api/questions', json={"searchTerm": "paintings"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data("questions")))

    def test_show_questions_by_category(self):
        res = self.client().get('/api/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data("questions")))

        res = self.client().get('/api/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertFalse(len(data("questions")))

    # def test_play_quiz(self):
    #     res = self.client().post('/api/quizzes', json={"previous_questions":[], "quiz_category": {"type": "Sports", "id": "6"}})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTure(len(data("questions")))
    #     self.assertEqual(data["questions"]["category"], 6)
    #
    # def test_play_quiz_no_questions(self):
    #     res = self.client().post('/api/quizzes', json={"previous_questions":[10, 11], "quiz_category": {"type": "Sports", "id": "6"}})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 405)
    #     self.assertFalse(len(data("questions")))



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
