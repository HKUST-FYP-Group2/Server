from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import unittest
import time

class TestLoginE2E(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
        self.driver.get("http://143.89.130.216:8080")  # URL of your Flask app

    def test_login(self):
        driver = self.driver
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("password")
        driver.find_element(By.XPATH, "//button[text()='Login']").click()
        time.sleep(2)

        driver.find_element(By.ID, "message").send_keys("test message by selenium")
        driver.find_element(By.XPATH, "//button[text()='Send']").click()
        time.sleep(2)

        driver.find_element(By.XPATH, "//button[text()='Logout']").click()
        time.sleep(2)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()