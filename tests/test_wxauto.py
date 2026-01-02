
import sys
import os
# 获取项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 将 src 目录加入路径
sys.path.append(os.path.join(root_path, "src"))
# 关键一步：将嵌套的 wxauto 源码目录加入路径
# 这样 wxauto 内部代码执行 "from wxauto import ..." 时才能找到自己
sys.path.append(os.path.join(root_path, "src", "wxauto"))

from wxauto import WeChat
wx = WeChat()
wx.SendMsg("你好", who="文件传输助手")