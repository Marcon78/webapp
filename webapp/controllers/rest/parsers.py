from flask_restful import reqparse


user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument("username", type=str, required=True)
user_post_parser.add_argument("password", type=str, required=True)

post_get_parser = reqparse.RequestParser()
# add_argument 参数：
#   action：声明了当参数值成功传入后，解析器进行何种后续操作。可选项为 store 和 append。默认为 store。
#           store  —— 把解析后的值放入返回的字典中。
#           append —— 把解析后的值放入一个列表中，并加入返回的字典。
#   case_sensitive：参数是否大小写敏感。布尔值。默认为 True。
#   choices：提供一个可选列表。
#   default：无参数传入时的默认值。
#   dest：加入返回的字典时所使用的键名。
#   help：如果参数不符合要求，则会向用户显示此信息。
#   ignore：当类型检查失败时是否返回错误。布尔值。默认为 False。
#   location：指出应该从哪里寻找所需的数据。可选项如下：
#           args    —— 在 GET 参数字符串中查找。
#           headers —— 在 HTTP 请求头中查找。
#           form    —— 在 HTTP 的 POST 表单数据中查找。
#           cookies —— 在 HTTP 的 cookie 中查找。
#           json    —— 在传入的任何 JSON 数据中查找。
#           files   —— 在 POST 的文件域中查找。
#   required：是否为可选参数。布尔值。默认为 False。
#   store_missing：当请求中缺失该参数时是否使用默认值进行填充。布尔值。默认为 True。
#   type：将传入的参数值转换成何种 Python 类型。
post_get_parser.add_argument("page", type=int, location=["args", "headers"])
post_get_parser.add_argument("user", type=str, location=("json", "args", "headers"))

post_post_parser = reqparse.RequestParser()
post_post_parser.add_argument("token", type=str, required=True,
                              help="Auth token is required to create posts")
post_post_parser.add_argument("title", type=str, required=True,
                              help="Title is required")
post_post_parser.add_argument("text", type=str, required=True,
                              help="Body text is required")
post_post_parser.add_argument("tags", type=str,
                              action="append")

# 每项修改都是可选的，因此，除了 token，其他所有字段的 required 参数保持 False。
post_put_parser = reqparse.RequestParser()
post_put_parser.add_argument("token", type=str, required=True,
                             help="Auth token is required to edit posts")
post_put_parser.add_argument("title", type=str)
post_put_parser.add_argument("text", type=str)
post_put_parser.add_argument("tags", type=str, action="append")


post_delete_parser = reqparse.RequestParser()
post_delete_parser.add_argument("token", type=str, required=True,
                                help="Auth token is required to delete posts")


comment_put_parser = reqparse.RequestParser()
comment_put_parser.add_argument("token", type=str, required=True,
                                help="Auth token is required to edit comments")
comment_put_parser.add_argument("text", type=str)
