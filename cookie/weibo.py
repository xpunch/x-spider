import os
import sys
import pymongo
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.getcwd())
from xspider.settings import MONGO_HOST, MONGO_PORT, MONGO_DATABASE, MONGO_USERNAME, MONGO_PASSWORD

class WeiboLogin():
    def __init__(self, username, password):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(1050, 840)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def run(self):
        self.open()
        WebDriverWait(self.browser, 30).until(EC.title_is('我的首页'))
        cookies = self.browser.get_cookies()
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        cookie_str = '; '.join(item for item in cookie)
        self.browser.quit()
        return cookie_str

if __name__ == '__main__':
    with open(os.getcwd() + '/cookie/weibo.txt', 'r') as file:
        lines = file.readlines()
    db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)[MONGO_DATABASE]
    db.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
    collection = db["weibo.cookies"]
    for line in lines:
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        try:
            cookie = WeiboLogin(username, password).run()
        except Exception as e:
            print("[ERR]Login failed:", username, e)
            continue
        try:
            collection.insert_one({"_id": username, "password": password, "cookie": cookie, "status": "success"})
        except DuplicateKeyError as e:
            collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie, "status": "success"}})