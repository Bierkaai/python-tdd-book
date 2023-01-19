from django.http import HttpRequest, request
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page


NEW_ITEM_TEXT = "A new list item"


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_can_save_a_POST_request(self):
        response = self.client.post("/", data={"item_text": NEW_ITEM_TEXT})
        self.assertIn(NEW_ITEM_TEXT, response.content.decode())
        # should still be using the home template
        self.assertTemplateUsed(response, 'home.html')
