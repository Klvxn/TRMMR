from unittest import TestCase

from app import app
from database import db
from urls.models import ShortenedURL


test_url = "https://www.bing.com/search?q=getdp&cvid=109e6e37d81c4c3f8f4587b0b9cc934b&aqs=edge.0.0l9.7054j0j4&FORM=ANAB01&PC=EE24"


class AppTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///testDB"
        cls.app.config["PREFERRED_URL_SCHEME"] = "http"
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def test_shorten_url(self):
        data = {"long_url": test_url}
        response = self.client.post("/", data=data)
        assert response.status_code == 200

    def test_customize_short_url(self):
        data = {"long_url": test_url, "custom_half": "example test url"}
        response = self.client.post("/", data=data)
        assert response.status_code == 200
        print(response.text)
        assert 'http://localhost/example-test-url' in response.get_data(as_text=True)
        
    def test_short_url_redirects_to_original_url(self):
        url = ShortenedURL.query.all()[0]
        response = self.client.get(url.short_url)
        assert response.status_code == 302 # 302 is the status code for redirects
        
    def test_sign_up(self):
        data = {
            "email_address": "go-david@gmail.com",
            "first_name": "David",
            "last_name": "Goliath",
            "password": "12345678"
        }
        response = self.client.post("/create-new-account/", data=data)
        assert response.status_code == 200

    def test_login(self):
        data = {
            "email_address": "go-david@gmail.com",
            "password": "12345678"
        }
        response = self.client.post("/log-in/", data=data)
        assert response.status_code == 200
        