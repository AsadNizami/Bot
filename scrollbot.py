import argparse
from time import sleep, time
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException
from urllib3.exceptions import MaxRetryError
import credentials as cred
from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


class ScrollBot:
    EXE_PATH = r'.\Utility\chromedriver'
    USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    PROCESSED = set()
    SCROLL_OFFSET = 690

    def __init__(self, username, password, max_like=7):
        self.username = username
        self.password = password
        self.max_like = max_like
        self.driver = self.configure()
        self.actions = ActionChains(self.driver)
        self.all_posts = list()
        self.current_position = 0
        self.start()

    def get_posts(self):
        start = time()
        x_like = '_8-yf5'
        self.all_posts = list()
        posts = self.driver.find_elements_by_class_name(x_like)
        try:
            for post in posts:
                if (post.get_attribute('aria-label') == 'Like' or post.get_attribute('aria-label') == 'Unlike')\
                        and post.get_attribute('height') == '24' and post.location['y'] not in self.PROCESSED and \
                        post.location['y'] != 0 and post.location['x'] != 0:
                    self.all_posts.append(post)
                    self.PROCESSED.add(post.location['y'])
        except MaxRetryError:
            self.driver.quit()
            print('All for now')
        print('Location for all post!')
        for post in self.all_posts:
            print(f'{post.location=}')
        print('length of all posts:', len(self.all_posts))
        end = time()
        print('Time taken(s) to find the elements:', end-start)
        if len(self.all_posts) < 1:
            self.driver.quit()
            print('No more post')
            exit()
        sleep(2)

    def start(self):

        self.login()
        num_processed = 0
        while num_processed < self.max_like:
            self.get_posts()
            num_processed += self.like_util()
            print('Number processed:', num_processed)
        print('Completed:', num_processed)

    def like_util(self):
        for post in self.all_posts:
            self.like(post)
        return len(self.all_posts)

    def configure(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={self.USER_AGENT}")
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        driver = webdriver.Chrome(executable_path=self.EXE_PATH, chrome_options=options)
        driver.maximize_window()
        return driver

    def wait(self, element, elementID):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((element, elementID))
            )
        except:
            print("Something's wrong. Check your internet connection")
            self.driver.quit()

    def login(self):
        self.driver.get('https://www.instagram.com/')
        x_username = r'//*[@id="loginForm"]/div/div[1]/div/label/input'
        x_password = r'//*[@id="loginForm"]/div/div[2]/div/label/input'
        self.wait(By.XPATH, x_username)

        username_input = self.driver.find_element_by_xpath(x_username)
        username_input.send_keys(self.username)
        password_input = self.driver.find_element_by_xpath(x_password)
        password_input.send_keys(self.password)

        self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div/div[3]').click()
        sleep(3)
        self.check_not_now()
        print('Logged In')
        sleep(3)

    def check_not_now(self):
        try:
            while True:
                self.driver.find_element_by_xpath(
                    "//button[contains(text(), 'Not Now')]").click()
                sleep(3)

        except common.exceptions.NoSuchElementException:
            pass

    def scroll(self, element):
        print(f'{self.current_position=} {element.location=}')
        required_position = element.location
        y = required_position['y']
        if y < self.current_position:
            print('Stale element encountered, post skipped')
            return
        while True:
            self.driver.execute_script("window.scrollTo(0, " + str(self.current_position) + ")")
            sleep(0.4)
            self.current_position += 50
            if self.current_position + self.SCROLL_OFFSET >= y:
                print('Current position:', y)
                sleep(3)
                return

    def like(self, current_post):
        print(f'Current post:', current_post.location['y'])
        self.scroll(current_post)
        sleep(1)
        post_status = current_post.get_attribute('fill')
        new_action = ActionChains(self.driver)
        try:
            print('Current action:', current_post.get_attribute('aria-label'))
            if current_post.location['y'] < self.current_position:
                return
            new_action.move_to_element_with_offset(current_post, 40, -50).click_and_hold().perform()
            new_action.release().perform()
            sleep(5)
            if post_status != '#ed4956':
                current_post.click()
                print(f'Post Liked {self.current_position=} {current_post.location=}')

        except StaleElementReferenceException as err:
            print('Last Coordinates:', self.current_position)
            print('Stale Element Encountered, post skipped\n', err)
        except ElementNotInteractableException:
            print('Could not interact with element at location y=', current_post.location['y'])
        sleep(3)


def get_args():
    parser = argparse.ArgumentParser(description='Scroll Bot Instagram')
    parser.add_argument('--total_like', help='Total number of posts to like', type=int)
    return parser.parse_args()


if __name__ == '__main__':
    like = get_args().total_like
    bot = ScrollBot(cred.username, cred.password, like)
