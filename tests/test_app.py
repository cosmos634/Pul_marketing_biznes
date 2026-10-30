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

    def test_lesson_four_has_quiz(self):
        response=self.client.get("/api/lesson/4")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.get_json()["questions"]),3)

    def test_note_can_be_saved(self):
        response=self.client.post("/api/note/4",json={"body":"Sinov qaydi"})
        self.assertEqual(response.status_code,200)
        saved=self.client.get("/api/lesson/4").get_json()["note"]
        self.assertEqual(saved,"Sinov qaydi")

if __name__=="__main__":
    unittest.main()
