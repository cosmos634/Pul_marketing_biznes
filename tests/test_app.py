import unittest
from app import app

class AcademyTests(unittest.TestCase):
    def setUp(self):
        self.client=app.test_client()

    def test_dashboard_loads(self):
        response=self.client.get("/")
        self.assertEqual(response.status_code,200)
        self.assertIn("Biznes Akademiya",response.get_data(as_text=True))

    def test_curriculum_has_thirty_days(self):
        response=self.client.get("/api/lessons")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.get_json()),30)

    def test_lesson_four_has_complete_content_and_quiz(self):
        response=self.client.get("/api/lesson/4")
        self.assertEqual(response.status_code,200)
        lesson=response.get_json()
        self.assertTrue(lesson["title"])
        self.assertTrue(lesson["theory"])
        self.assertTrue(lesson["example"])
        self.assertTrue(lesson["task"])
        self.assertEqual(len(lesson["questions"]),3)

    def test_all_thirty_lessons_have_content(self):
        response=self.client.get("/api/lessons")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.get_json()),30)
        for item in response.get_json():
            lesson=self.client.get(f'/api/lesson/{item["day"]}').get_json()
            self.assertTrue(lesson["title"])
            self.assertTrue(lesson["theory"])
            self.assertTrue(lesson["example"])
            self.assertTrue(lesson["visual"])
            self.assertTrue(lesson["task"])
            self.assertEqual(len(lesson["questions"]),3)

    def test_quiz_submission(self):
        lesson=self.client.get("/api/lesson/4").get_json()
        answers={str(q["id"]):0 for q in lesson["questions"]}
        response=self.client.post("/api/quiz/4",json={"answers":answers})
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.get_json()["passed"])
        self.assertEqual(response.get_json()["score"],100)

    def test_note_can_be_saved(self):
        response=self.client.post("/api/note/4",json={"body":"Sinov qaydi"})
        self.assertEqual(response.status_code,200)
        saved=self.client.get("/api/lesson/4").get_json()["note"]
        self.assertEqual(saved,"Sinov qaydi")

if __name__=="__main__":
    unittest.main()
