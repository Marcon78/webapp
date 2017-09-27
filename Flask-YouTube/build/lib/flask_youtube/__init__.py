from flask import Blueprint, render_template, Markup


class Video(object):
    def __init__(self, video_id, cls="youtube"):
        self.video_id = video_id
        self.cls = cls

    def render(self, *args, **kwargs):
        return render_template(*args, **kwargs)

    @property
    def html(self):
        # 使用 Markup 转义 HTML，避免 Jinja2 自动转义。
        # 这是 Flask 保护免受跨站脚本攻击 —— Cross-Site Scripting (XSS) attack —— 的方式。
        return Markup(self.render("youtube/video.html", video=self))


def youtube(*args, **kwargs):
    video = Video(*args, **kwargs)
    return video.html


class Youtube(object):
    def __init__(self, app=None, **kwargs):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.register_blueprint(app)
        # 将自定义函数添加到 Jinja2 全局作用域中。
        # https://stackoverflow.com/questions/29257476/how-can-i-make-a-class-variable-available-to-jinja2-templates-with-flask
        # 在 Flask 框架中，把变量注册到全局，有两个方法：
        # 1、在主 app 或者蓝本中通过装饰器注册：
        #     @app.context_processor
        #     def include_permission_class():
        #         return {'Permission': Permission}
        # 2、添加到 jinja2 的全局名称空间中：
        #     app.add_template_global(Permission, 'Permission')
        # app.add_template_global() 方法的第一个参数是自定义的全局函数，第二个是全局函数名称。
        app.add_template_global(youtube)

    def register_blueprint(self, app):
        module = Blueprint("youtube",
                           __name__,
                           template_folder="templates")
        app.register_blueprint(module)
        return module


# youtube_ext = Youtube()