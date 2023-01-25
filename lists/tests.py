from django.http import HttpRequest, request
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page

from lists.models import Item, List

NEW_ITEM_TEXT = "A new list item"

FIRST_ITEM_TEXT = "The first (ever) list item"
SECOND_ITEM_TEXT = "Item the second"

OTHER_LIST_ITEM_1 = "other list item 1"
OTHER_LIST_ITEM_2 = "other list item 2"

NEW_ITEM_EXISTING_LIST = "A new item for an existing list"


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = FIRST_ITEM_TEXT
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = SECOND_ITEM_TEXT
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_item.text, FIRST_ITEM_TEXT)
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_item.text, SECOND_ITEM_TEXT)
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text=FIRST_ITEM_TEXT, list=correct_list)
        Item.objects.create(text=SECOND_ITEM_TEXT, list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text=OTHER_LIST_ITEM_1, list=other_list)
        Item.objects.create(text=OTHER_LIST_ITEM_2, list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")

        self.assertContains(response, FIRST_ITEM_TEXT)
        self.assertContains(response, SECOND_ITEM_TEXT)

        self.assertNotContains(response, OTHER_LIST_ITEM_1)
        self.assertNotContains(response, OTHER_LIST_ITEM_2)

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertEqual(response.context['list'], correct_list)


class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        # Posting an item to the /lists/new API endpoint
        self.client.post("/lists/new", data={"item_text": NEW_ITEM_TEXT})
        # Checking that there is now an instance of Item
        self.assertEqual(Item.objects.count(), 1)
        # Getting the item
        new_item = Item.objects.first()
        # Checking it has the same text as we sent to the API
        self.assertEqual(new_item.text, NEW_ITEM_TEXT)

    def test_redirects_after_POST(self):
        response = self.client.post("/lists/new", data={"item_text": NEW_ITEM_TEXT})
        new_list = List.objects.first()
        self.assertRedirects(response, f"/lists/{new_list.id}/")


class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/add_item",
            data={"item_text": NEW_ITEM_EXISTING_LIST},
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, NEW_ITEM_EXISTING_LIST)
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        _ = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f"/lists/{correct_list.id}/add_item",
            data={"item_text": NEW_ITEM_EXISTING_LIST},
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")
