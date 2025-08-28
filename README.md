# torchsearch
####警告！！！

1.只有此仓库和发行版是作者正版，如有其它版本，均为盗版，所产生的一切后果，与作者无关
2.本工具只作为查询用处，推荐的安装命令仅供参考，如果对开发环境、硬件造成损坏，后果由使用者自负
3.此工具仅供学习交流，请勿商用
4.下载、使用、修改、重新打包本工具视为已经认可警告

#### 介绍
一种通过手动或自动输入cuda版本,推荐匹配的pytorch相关组件包版本的查询工具

# 🎯 PyTorch CUDA 版本匹配助手

一个简单易用的图形化工具，帮助你快速找到与当前 CUDA 版本兼容的 `torch`、`torchvision` 和 `torchaudio` 安装命令。

✅ 支持自动检测 `nvcc`  
✅ 手动输入 CUDA 版本  
✅ 一键复制 pip 安装命令  
✅ 无需 Python 环境，打包为独立 `.exe` 可执行文件  
✅ 支持 CUDA 10.2 ~ 12.9（自动映射到官方构建版本）

---

## 📦 下载与使用（无需开发环境）

> 适合不会命令行的用户、学生、团队分发

1. 下载 [`torch_cuda_gui.exe`](https://gitee.com/stevenjsp/torchsearch/releases/download/0.0.1/torch_cuda_gui.exe)（最新发布版）
2. 双击运行（Windows 11）
3. 点击 **🔍 自动检测 nvcc** 或手动输入 CUDA 版本（如 `11.8`）
4. 点击 **🚀 开始匹配**
5. 点击 **📋 复制安装命令**，粘贴到你的终端执行

> ⚠️ 首次运行杀毒软件可能误报，请添加信任或关闭实时防护。

---

## 🛠 开发者指南（源码构建）

如果你希望修改或重新打包本工具，请参考以下步骤。

### 1. 克隆项目

git clone https://gitee.com/stevenjsp/torchsearch.git
cd torch-cuda-gui

### 2.安装依赖

pip install -r requirements.txt

requirements.txt 内容：
pyperclip
pillow  # 用于图标生成（可选）
tkinter 是 Python 内置库，无需安装。

### 3. 运行 Python 脚本

python torch_cuda_gui.py

📦 打包为 .exe（Windows）
1. 安装 PyInstaller

pip install pyinstaller

2. 准备 Tcl/Tk 支持文件（关键！避免启动报错）
复制你的 Python 安装目录下的 tcl 文件夹到项目根目录：

D:\Python313\tcl\  -->  G:\torchsearch\tcl\
确保包含 tcl8.6 和 tk8.6 子目录。

3. 生成图标（可选）
运行：

python generate_icon.py
生成 icon.ico 图标文件。

4. 打包命令

pyinstaller --onefile --windowed 
    --add-data "tcl;tcl" 
    --icon=icon.ico 
    torch_cuda_gui.py
打包完成后，可执行文件位于 dist/torch_cuda_gui.exe。

🔧 支持的 CUDA 版本映射
CUDA 版本	PyTorch 构建标签	推荐 torch 版本
10.2	cu102	1.13.1
11.3	cu113	1.13.1
11.6	cu116	1.13.1
11.7	cu117	2.0.1
11.8	cu118	2.1.2
12.1	cu121	2.2.2
12.4~12.9	cu121 ✅	2.3.1 ~ 2.4.1
📌 说明：CUDA 12.4 及以上版本（包括 12.5~12.9）均使用 cu121 构建，只要驱动支持即可正常运行。

❓ 常见问题
Q: 运行 .exe 报错 “Can't find a usable init.tcl”？
A: 请确保打包时包含了 tcl 文件夹，并使用 --add-data "lib;tcl" 参数。

Q: 为什么没有 cu124 或 cu128 的 PyTorch 包？
A: PyTorch 官方目前只发布 cu121 构建，它兼容 CUDA 12.1+，无需单独版本。

Q: 如何检查我的 CUDA 驱动支持的最高版本？
A: 运行 nvidia-smi，右上角显示的 “CUDA Version” 即为驱动支持的最高版本。

📎 依赖与许可
使用 tkinter 构建 GUI
打包工具：PyInstaller
图标生成：Pillow
开源协议：GPL-3.0

