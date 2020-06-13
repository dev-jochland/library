from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_visit_site_and_view_books(self):
        # Edith has heard about a cool local library, she goes to
        # check out its homepage
        self.browser.get('http://localhost:8000')

        # She notices the page title and header mention 'Home'
        self.assertIn('Home', self.browser.title)

        # This below fails no matter what, producing the error message given.
        # It's a reminder to finish the test
        self.fail('Finish title test')


# This below allows a python script to check if it's been executed from the
# command line rather than just imported by another script.
# unittest.main() launches the unittest test runner
if __name__ == '__main__':
    unittest.main()
