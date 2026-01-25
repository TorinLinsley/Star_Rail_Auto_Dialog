# 星铁自动过剧情脚本工具
功能：自动对话，自动选择对话句子，如果有跳过按钮会直接点跳过按钮跳过。

> 采用 Python的**opencv**库进行图像识别来实现自动化点击操作，以及使用了**threading**库 多线程，对每个功能独立处理，相互不堵塞。

## 注意事项
- **跳过剧情功能 建议仅在过剧情对话时开启**，点击跳过按钮，跳过剧情确认弹窗靠的是识别确认按钮的按钮内区域，如果是其它界面可能也会自动点。
- 使用**python.exe**运行代码，而不是pythonw.exe

运行脚本前确保安装了`requirements.txt`中提到的库，不然不能正常运行脚本。

需要安装的话可以使用以下命令安装`requirements.txt`写到的库：（在`requirements.txt`所在位置打开终端/cmd执行）

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 其它说明

在`recognition.py`代码里643到651行中的_register_functions函数里可以设置哪些功能在程序启动时是否为默认启动状态。


>  "codename": {"hotkey": "shortcut", "type": "type", "func": "(main)function name", "running": "whether to start by default"}

**在发行(Release)中：**

- Star-Rail_Auto_Dialog 的zip压缩包为直接打包的源代码程序。
- Star-Rail_Auto_Dialog_Excutable 的zip压缩包为由代码打包好的exe可执行程序。
