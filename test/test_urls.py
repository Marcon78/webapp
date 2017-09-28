# 测试路由函数
from unittest import TestCase, main

from webapp import create_app
from webapp.models import db, User, Role
from webapp.extensions import rest_api

class TestURLs(TestCase):
    def setUp(self):
        # 修复 bug 的方法：
        # Flask Restful 扩展会为应用生成蓝图对象并在内部保存起来，但是在应用销毁时不会主动将其移除。
        rest_api.resources = []

        self.app = create_app("webapp.config.TestConfig")
        self.app_context = self.app.app_context()
        # Flask 在分发请求之前激活（或推入）程序和请求上下文，请求处理完成后再将其删除。
        # 程序上下文被推送后，就可以在线程中使用 current_app 和 g 变量。
        self.app_context.push()
        self.client = self.app.test_client()

        # # 修复 bug 的方法：
        # db.app = self.app
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # 删除（弹出）程序上下文。
        self.app_context.pop()

    # 每个单元测试的名字都必须以 test 开始，这样 unittest 库就会将其视为一个单元测试，而不是一个普通函数。
    # 为单元测试加上 Python 文档字符串，无论何时测试失败，文档会和测试的名字一起被打印出来。
    def test_root_redirect(self):
        """检测根路径是否返回了 302。"""
        result = self.client.get("/")
        # 检查响应的状态码是否为 302，这个代码表示重定向。
        # self.assertTrue(result.status_code == 302)
        self.assertEqual(result.status_code, 302)
        self.assertIn("/blog/", result.headers["Location"])

    def test_login(self):
        """测试登录窗体是否正常工作。"""
        test_role = Role("DEFAULT")
        db.session.add(test_role)
        db.session.commit()

        test_user = User("test", "test")
        db.session.add(test_user)
        db.session.commit()

        # 参数 follow_redirects=True，让测试客户端和浏览器一样，自动向重定向的 URL 发起 GET 请求。
        result = self.client.post("/login",
                                  data=dict(
                                      username="test",
                                      password="test"),
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been logged in", str(result.data))

        # 注意，这里没有数据提交，因此使用 get()。
        result = self.client.get("/logout",
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been logged out", str(result.data))


# 测试需要在“父”目录而不是测试用例目录中运行，这样可以方便地在测试代码中直接导入应用内的代码。
# 运行
# python -m unittest discover
if __name__ == "__main__":
    main()
