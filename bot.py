from selenium import webdriver, common
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import credentials as cred

DATABASE = dict()


class Bot:
    PATH = r'.\Utility\chromedriver'
    USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    def __init__(self):
        self.driver = self.configure()
        self.login(cred.username, cred.password)
        self.check_not_now()

    def operation(self, username, action):
        if action == 'like':
            self.start_like(username)
        elif action == 'report':
            self.report(username)

        else:
            print('No')
        self.driver.close()

    def configure(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={self.USER_AGENT}")
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        driver = webdriver.Chrome(executable_path=self.PATH, chrome_options=options)
        driver.maximize_window()

        return driver

    def refresh(self):
        self.driver.refresh()
        sleep(3)

    def wait(self, element, elementID):
        try:
            react_root = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((element, elementID))
            )
        except:
            self.driver.quit()

    def start_like(self, username):
        self.all_post_user(username)
        self.like_comment(username)

    def login(self, username, password):
        self.driver.get('https://instagram.com/')
        sleep(2)
        xpath_username = '//*[@id="loginForm"]/div/div[1]/div/label/input'
        xpath_password = '//*[@id="loginForm"]/div/div[2]/div/label/input'
        self.wait(By.XPATH, xpath_username)

        username_input = self.driver.find_element_by_xpath(xpath_username)
        username_input.send_keys(username)

        password_input = self.driver.find_element_by_xpath(xpath_password)
        password_input.send_keys(password)

        self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div/div[3]').click()
        sleep(3)

    def check_not_now(self):
        try:
            while True:
                self.driver.find_element_by_xpath(
                    "//button[contains(text(), 'Not Now')]").click()
                sleep(3)

        except common.exceptions.NoSuchElementException:
            print('Thats all')

    def all_post_user(self, username):

        self.driver.get(f'https://www.instagram.com/{username}/')
        sleep(2)
        while True:
            if 'Oops, an error occurred.' == self.driver.find_element_by_tag_name('body').text:
                print('Refreshing')
                self.refresh()
            else:
                break
        if username not in DATABASE:
            DATABASE[username] = list()

        all_links_in_page = self.driver.find_elements_by_tag_name('a')

        def condition(link):
            return '.com/p/' in link.get_attribute('href')

        post_link = list(filter(condition, all_links_in_page))
        for post in post_link:
            link = post.get_attribute('href')
            print('Link', link)
            DATABASE[username].append(link)

    def like_comment(self, username):
        links = DATABASE[username]

        for link in links:
            self.driver.get(link)
            self.wait(By.ID, 'react-root')
            while True:
                check_div = self.driver.find_element_by_id('react-root')
                if check_div.text == '':
                    self.refresh()
                    print('React ID Not found')
                else:
                    break
            try:
                self.driver.find_elements_by_class_name('wpO6b  ')[1].click()
            except common.exceptions.NoSuchElementException as err:
                print(err)
                self.refresh()

    def report(self, username):
        def start_report(driver):
            sleep(1)
            driver.find_element_by_class_name(dot_xpath).click()
            sleep(1)
            driver.find_element_by_xpath(report_user_xpath).click()
            sleep(1)
            driver.find_elements_by_class_name(report_account_xpath)[-1].click()
            sleep(1)
            driver.find_elements_by_class_name(first_option)[0].click()
            sleep(1)
            driver.find_elements_by_class_name(spam_xpath)[0].click()
            sleep(3)

        self.driver.get(f'https://www.instagram.com/{username}/')
        sleep(2)
        dot_xpath = 'wpO6b'
        report_user_xpath = "//button[contains(text(), 'Report User')]"
        report_account_xpath = 'b5k4S'  # "//button[contains(text(), 'Report Account')]"
        first_option = 'b5k4S'  # '//button[contains(text(), "It\'s posting content that shouldn\'t be on Instagram")]'
        spam_xpath = 'b5k4S'  # "//button[contains(text(), 'It's spam')]"

        for _ in range(2):
            try:
                start_report(driver=self.driver)
                break
            except common.exceptions.NoSuchElementException as err:
                print(err)
                self.refresh()


def get_args():
    parser = argparse.ArgumentParser(description='Automate instagram')
    parser.add_argument('--page', help='Target page')
    parser.add_argument('--operation', help='Action to perform')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    bot = Bot()
    bot.operation(args.page, args.operation)
