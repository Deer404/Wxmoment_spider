# -*- coding:utf-8 -*-
# author:Deer404
# contact: 919187569.com
# datetime:2019/7/25 21:24
# software: PyCharm

"""
文件说明：
    对微信朋友圈内容进行抓取并转换成词云图
"""
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymysql
import jieba  # jieba分词
import warnings
import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


class Wx_moment():
    def __init__(self):
        desired_caps = dict()
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '8'
        desired_caps['deviceName'] = '5d98874f'
        desired_caps['appPackage'] = 'com.tencent.mm'
        desired_caps['appActivity'] = '.ui.LauncherUI'
        desired_caps['noReset'] = 'True'
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
        # 设置等待
        self.wait = WebDriverWait(self.driver, 300)
        self.start_x = 300
        self.start_y = 1295
        self.end_x = 300
        self.end_y = 300
        self.db = pymysql.connect("localhost", "root",
                                  "123456", "wechat_moment")
        self.cursor = self.db.cursor()
        self.sql = '''create table if not exists moment( id int primary KEY auto_increment,name varchar(255) NOT NULL ,content varchar(255) NOT NULL,UNIQUE (content))'''
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.cursor.execute(self.sql)
        self.moment_text = ""
        print("微信启动")

    def enter_moment(self):
        # time.sleep(10)
        # btn = self.driver.find_element_by_xpath('//android.widget.TextView[@text="发现"]/../parent::android.widget.RelativeLayout')
        # btn.click()
        # find_location = btn.location
        # find_x = int(find_location['x'])
        # find_y = int(find_location['y'])
        # self.driver.tap([(find_x,find_y),(810,1920)],100)
        findBtn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.TextView[@text="发现"]/../parent::android.widget.RelativeLayout')))
        findBtn.click()
        momentBtn = self.wait.until(EC.element_to_be_clickable((By.ID, "com.tencent.mm:id/amc")))
        momentBtn.click()
        print("进入朋友圈")
        time.sleep(3)
        # content = self.driver.find_elements_by_xpath('//*[@resource-id="com.tencent.mm:id/et8"]')
        # print(content.get('1'))
        # mom = self.wait.until(EC.presence_of_element_located((By.ID,"com.tencent.mm:id/et8")))
        # self.driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, 2000)

    def swipes(self):
        self.driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, 2000)

    def get_moment(self, cyclesNum=30):
        """
        :param cyclesNum: 循环次数
        :return:
        """
        for i in range(1, cyclesNum + 1):
            items = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@resource-id="com.tencent.mm:id/eok"]//*[@class="android.widget.FrameLayout"]')))
            self.driver.swipe(300, 1000, 300, 300)
            for item in items:
                try:
                    nickname = item.find_element_by_id('com.tencent.mm:id/b95').get_attribute('text').strip()
                    print("姓名: " + nickname)
                    content = item.find_element_by_id('com.tencent.mm:id/etb').get_attribute('text').strip()
                    print("朋友圈内容: " + content.strip())
                    self.insert_to_db(nickname, content)
                except EC.WebDriverException:
                    pass

    def insert_to_db(self, name, content):
        """

        :param name: 朋友圈名字
        :param content: 朋友圈内容
        :return:
        """
        # print("插入数据库"+name+"|"+content)
        # insert_sql = """INSERT INTO moment(name,content)values(%s,%s) ON DUPLICATE KEY UPDATE content = %s;"""
        # self.cursor.execute(insert_sql, (name, content, content))
        ######################
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            insert_sql = """INSERT ignore INTO moment(name,content)values(%s,%s);"""
            self.cursor.execute(insert_sql, (name, content))
            #####################
            self.db.commit()

    def close_db(self):
        selectsql = 'select * from moment'
        self.cursor.execute(selectsql)
        self.cursor.close()

    def save_text(self):
        sql = "select * from moment"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for item in result:
            content = item[2]
            self.moment_text = self.moment_text + content
        # with open('data.txt', 'w+',encoding='UTF-8') as f:
        #     f.write(moment_string)
        cut_text = " ".join(jieba.cut(self.moment_text, cut_all=True))
        girl_img = np.array(Image.open('girl.png'))
        image_colors = ImageColorGenerator(girl_img)
        wordcloud = WordCloud(
            scale=10,
            mask=girl_img,
            font_path="C:/Windows/Fonts/simfang.ttf",
            max_words=150,
            max_font_size=60,
            background_color="white",
            width=1920,
            height=1080).generate(cut_text)
        wordcloud.recolor(color_func=image_colors)
        wordcloud.to_file("朋友圈内容词云.png")
        print("生成成功")

    def save_name(self):
        sql = "select * from moment"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for item in result:
            name = item[1]
            self.moment_text = self.moment_text + name
            jieba.add_word(name)  # 把朋友圈姓名加入分词词库 避免被分开
        # jieba.add_word("牛顿不是很喜欢苹果")
        cut_text = " ".join(jieba.cut(self.moment_text))
        girl_img = np.array(Image.open('girl.png'))
        image_colors = ImageColorGenerator(girl_img)
        wordcloud = WordCloud(
            scale=10,
            mask=girl_img,
            font_path="C:/Windows/Fonts/simfang.ttf",
            max_words=150,
            random_state=42,
            max_font_size=60,
            background_color="white",
            width=1920,
            height=1080).generate(cut_text)
        wordcloud.recolor(color_func=image_colors)
        wordcloud.to_file("朋友圈名字词云.png")
        print("生成成功")

    # def convert_to_wordcloud(self): #生成词云方法 已经内置在save_to_xx方法里 不需要单独使用
    #     print("生成词云中")
    #     cut_text = " ".join(jieba.cut(self.moment_text))
    #     girl_img = np.array(Image.open('girl.png'))
    #     image_colors = ImageColorGenerator(girl_img)
    #     wordcloud = WordCloud(
    #         scale=10,
    #         mask=girl_img,
    #         font_path="C:/Windows/Fonts/simfang.ttf",
    #         max_words=150,
    #         random_state=42,
    #         max_font_size=60,
    #         background_color="white",
    #         width=1920,
    #         height=1080).generate(cut_text)
    #     # plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
    #     wordcloud.recolor(color_func=image_colors)
    #     wordcloud.to_file("词云.png")
    #     # plt.axis("off")
    #     # plt.savefig("词云.png")
    #     # plt.show()
    #     print("生成成功")

    def run(self, num=30, mode=1):
        """

        :param num: 循环次数 差不多就是滑动多少次
        :param mode: 共两个参数(1和2 ) 1是生成朋友圈内容词云 2是生成朋友圈名字词云
        :return:
        """
        self.enter_moment()
        self.get_moment(num)
        if mode == 1:
            self.save_text()
        if mode == 2:
            self.save_name()
        self.close_db()

    def wipe_data(self):  # 清除表数据 不可撤回噢
        deletesql = "truncate table moment"
        self.cursor.execute(deletesql)
        self.db.commit()


if __name__ == "__main__":
    wx = Wx_moment()
    wx.run(200, 1)
