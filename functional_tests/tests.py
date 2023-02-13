from email import header
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import unittest
import time

import os

FIRST_ITEM_TEXT = "Buy peacock feathers"
SECOND_ITEM_TEXT = "Use peacock feathers to make a fly"
FRANCIS_FIRST_TEXT = "Buy milk"

LIST_URL_REGEX = r"/lists/.+"

# How many seconds should we wait for the page to load before failing the test?
MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        staging_server = os.environ.get('STAGING_SERVER')  
        if staging_server:
            self.live_server_url = 'http://' + staging_server
        self.browser = webdriver.Chrome()

    def tearDown(self) -> None:
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id("id_list_table")
                rows = table.find_elements_by_tag_name("tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.2)

    @unittest.skip
    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        browser_size = self.browser.get_window_size()
        

        # She notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + (inputbox.size["width"] / 2), browser_size['width'], delta=20
        )

        # She starts a new list and sees the input is nicely
        # centered there too
        inputbox.send_keys(FIRST_ITEM_TEXT)
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(f"1: {FIRST_ITEM_TEXT}")
        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + (inputbox.size["width"] / 2), browser_size['width'], delta=20
        )

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its home page
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn("To-Do", header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a to-do item")

        # She types "Buy peacock feathers" into a text box
        inputbox.send_keys(FIRST_ITEM_TEXT)

        # When she hits "Enter", the page updates, and not the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(f"1: {FIRST_ITEM_TEXT}")

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly"
        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys(SECOND_ITEM_TEXT)
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table(f"1: {FIRST_ITEM_TEXT}")
        self.wait_for_row_in_list_table(f"2: {SECOND_ITEM_TEXT}")

        # Satisfied, she goes back to sleep

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith starts a new to-do list
        self.browser.get(self.live_server_url)

        # She enters a to-do item
        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys(FIRST_ITEM_TEXT)
        inputbox.send_keys(Keys.ENTER)

        # It appears in the to-do list on the website
        self.wait_for_row_in_list_table(f"1: {FIRST_ITEM_TEXT}")

        # She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, LIST_URL_REGEX)

        # Now a new user, Francis comes along to the site.

        ## We use a new browser session to make sure that no information
        ## of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn(FIRST_ITEM_TEXT, page_text)
        self.assertNotIn(SECOND_ITEM_TEXT, page_text)

        # Francis startes a new list by entering a new item. He is less
        # interesting than Edith
        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys(FRANCIS_FIRST_TEXT)
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table(f"1: {FRANCIS_FIRST_TEXT}")

        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, LIST_URL_REGEX)
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again , there is no trace of Edith's list
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn(FIRST_ITEM_TEXT, page_text)
        self.assertIn(FRANCIS_FIRST_TEXT, page_text)

        # Satisfied, they both go back to sleep
