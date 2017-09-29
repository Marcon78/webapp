import threading
import time
from unittest import TestCase
#http://selenium-python.readthedocs.io/
from selenium import webdriver

from webapp import create_app
from webapp.models import db, User, Role
# from webapp.extensions import rest_api


# Selenium 中的两个陷阱：
# 1、Selenium 的工作方式是模拟一个正在操作浏览器的人，这就意味着如果一个元素在页面上是不可见的，那么 Selenium 就无法与之交互。
#    诸如被遮挡的元素，CSS 样式中 display 被设置为 none，或者 visibility 被设置为 hidden。
# 2、所有指向屏幕上的元素的变量，都是以指向这些浏览器中元素的引用的形式存储的，并没有在 Python 内存中独立保存。
#    如果没有使用 get() 方法，而使页面发生了变化，例如单击了一个链接从而创建了一个新的元素指针，则测试会崩溃。
#    原因在于驱动(driver)会不断地查找属于之前那个元素上的元素，但是在新页面上无法找到它们。
#    使用驱动的 get() 方法就可以清理掉所有这些引用。
#
# 其他参考：
#     Selenium 是开源的 web 自动测试工具，免费，主要做功能测试。
#     Loadrunner 是商业性能测试工具，收费，功能强大，适合做复杂场景的性能测试。
#     QTP 是商业的功能测试工具，收费，支持 web，桌面自动化测试，貌似移动端也能做。
#     jmeter
#     silktest

class TestURLs(TestCase):
    # # 修复 bug 的方法：
    # # Flask Restful 扩展会为应用生成蓝图对象并在内部保存起来，但是在应用销毁时不会主动将其移除。
    # rest_api.resources = []

    # 定义一个类变量，保存 webdriver。
    client = None

    # 将原文中 setUp() 的逻辑放到这里
    # setUpClass() 类方法在这个类中的全部测试运行前执行。
    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # 替代原文中 run_test_server.py 的作用。
        if cls.client:
            # 创建应用
            cls.app = create_app("webapp.config.TestConfig")
            if not cls.app:
                print("My Error")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 抑制日志记录，保持单元测试的输出内容干净。
            import logging
            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")

            # 初始化数据库，添加测试数据。
            db.create_all()

            roles = ["ADMINISTRATOR", "AUTHOR", "DEFAULT"]
            for r in roles:
                if not Role.query.filter_by(name=r).first():
                    new_role = Role(r)
                    db.session.add(new_role)
            db.session.commit()

            poster = Role.query.filter_by(name="AUTHOR").one()

            test_user = User.query.filter_by(username="test").first()
            if not test_user:
                test_user = User("test")
                test_user.set_password("test")
                test_user.roles.append(poster)
                db.session.add(test_user)
                db.session.commit()

            # 在另一个线程中启动 Flask 服务器。该线程需要在 tearDownClass() 中通过 shutdown 路由关闭。
            # threading.Thread(target=cls.app.run, kwargs={"port": default_port}).start()
            threading.Thread(target=cls.app.run).start()

            # 等待 1 秒钟，让 Flask 服务器启动。
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 通过 shutdown 路由关闭 Flask 服务器。
            cls.client.get("http://localhost:5000/shutdown")
            cls.client.close()

            db.session.remove()
            db.drop_all()

            cls.app_context.pop()

    def setUp(self):
        # 此处的 driver 是类变量
        if not self.client:
            self.skipTest("Web browser not available")

    def tearDown(self):
        pass

    def testDummy(self):
        self.assertTrue(1==1)

    # def test_add_new_post(self):
    #     """测试是否可使用文章创建页面新增一篇文章
    #
    #         1、用户登录网站。
    #         2、前往新文章创建页面。
    #         3、填写表单各域，并提交表单。
    #         4、前往博客首页，确认这篇新文章出现在首页。
    #     """
    #
    #     # 登录
    #     self.client.get("http://127.0.0.1:5000/login")
    #
    #     username_field = self.client.find_element_by_name("username")
    #     username_field.send_keys("test")
    #
    #     password_field = self.client.find_element_by_name("password")
    #     password_field.send_keys("test")
    #
    #     login_button = self.client.find_element_by_id("login_button")
    #     login_button.click()
    #
    #     # 填写数据
    #     self.dirver.get("http://127.0.0.1:5000/blog/new")
    #     title_field = self.client.find_element_by_name("title")
    #     title_field.send_keys("Test Title")
    #
    #     # 在 iframe 中查找编辑器
    #     self.client.switch_to.frame(
    #         self.client.find_element_by_tag_name("iframe")
    #     )
    #     post_field = self.client.find_element_by_class_name("cke_editable")
    #     post_field.send_keys("Test Content")
    #     self.client.switch_to.parent_frame()
    #
    #     post_button = self.client.find_element_by_class_name("btn-primary")
    #     post_button.click()
    #
    #     # 确认文章已经创建
    #     self.client.get("http://127.0.0.1:5000/blog")
    #     self.assertIn("Test Title", self.client.page_source)
    #     self.assertIn("Test Content", self.client.page_source)
