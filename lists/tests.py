from django.http import HttpRequest, request
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page

from lists.models import Item

NEW_ITEM_TEXT = "A new list item"

FIRST_ITEM_TEXT = "The first (ever) list item"
SECOND_ITEM_TEXT = "Item the second"


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
        self.assertTemplateUsed(response, "home.html")


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        first_item = Item()
        first_item.text = FIRST_ITEM_TEXT
        first_item.save()

        second_item = Item()
        second_item.text = SECOND_ITEM_TEXT
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_item.text, FIRST_ITEM_TEXT)
        self.assertEqual(second_item.text, SECOND_ITEM_TEXT)
