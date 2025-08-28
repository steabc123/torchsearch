import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
import subprocess
import os


def get_nvcc_version():
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, check=True)
        output = result.stdout
        match = re.search(r'release (\d+\.\d+)', output)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None


def get_torch_versions(cuda_version):
    version_map = {
        '10.2': ('1.13.1', '0.14.1', '0.13.1', 'cu102'),
        '11.3': ('1.13.1', '0.14.1', '0.13.1', 'cu113'),
        '11.6': ('1.13.1', '0.14.1', '0.13.1', 'cu116'),
        '11.7': ('2.0.1', '0.15.2', '0.15.1', 'cu117'),
        '11.8': ('2.1.2', '0.16.2', '2.1.2', 'cu118'),
        '12.1': ('2.2.2', '0.17.2', '2.2.2', 'cu121'),
        '12.4': ('2.3.1', '0.18.1', '2.3.1', 'cu121'),# cu121 兼容 12.4
        '12.5': ('2.4.1', '0.19.1', '2.4.1', 'cu121')
    }

    if cuda_version in version_map:
        return version_map[cuda_version]

    major = cuda_version.split('.')[0]
    fallback_map = {'11': '11.8', '12': '12.1'}
    if major in fallback_map:
        fallback_ver = fallback_map[major]
        if fallback_ver in version_map:
            return version_map[fallback_ver]
    return None


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 PyTorch CUDA 版本选择助手")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 标题
        title = tk.Label(root, text="PyTorch CUDA 版本适配器", font=("Microsoft YaHei", 16, "bold"))
        title.pack(pady=10)

        desc = tk.Label(root, text="选择 CUDA 版本，获取对应的 torch 安装命令", font=("Microsoft YaHei", 10))
        desc.pack(pady=5)

        # 输入框架
        frame = tk.Frame(root)
        frame.pack(pady=10, padx=20, fill="x")

        tk.Label(frame, text="CUDA 版本:", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.cuda_entry = tk.Entry(frame, width=20, font=("Courier", 12))
        self.cuda_entry.grid(row=0, column=1, padx=5, pady=5)

        self.auto_btn = tk.Button(frame, text="🔍 自动检测 nvcc", command=self.auto_detect, width=15)
        self.auto_btn.grid(row=0, column=2, padx=5)

        self.go_btn = tk.Button(frame, text="🚀 开始匹配", command=self.run_match, width=15)
        self.go_btn.grid(row=1, column=2, pady=10)

        # 输出区域
        result_frame = tk.Frame(root)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(result_frame, text="推荐版本与安装命令:", font=("Microsoft YaHei", 10, "bold")).pack(anchor="w")

        self.result_text = scrolledtext.ScrolledText(
            result_frame, height=10, font=("Courier", 10), state="disabled"
        )
        self.result_text.pack(fill="both", expand=True, pady=5)

        # 按钮
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.copy_btn = tk.Button(btn_frame, text="📋 复制安装命令", command=self.copy_command, state="disabled", width=20)
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="🗑 清空", command=self.clear_all, width=15)
        self.clear_btn.pack(side="left", padx=5)

        self.last_command = ""

    def auto_detect(self):
        ver = get_nvcc_version()
        if ver:
            self.cuda_entry.delete(0, tk.END)
            self.cuda_entry.insert(0, ver)
            messagebox.showinfo("✅ 成功", f"检测到 CUDA 版本: {ver}")
        else:
            messagebox.showwarning("⚠️ 失败", "未找到 nvcc 或无法解析版本。\n请手动输入 CUDA 版本。")

    def run_match(self):
        cuda_input = self.cuda_entry.get().strip()
        if not re.match(r'^\d+\.\d+$', cuda_input):
            messagebox.showerror("❌ 错误", "请输入有效的 CUDA 版本，如 11.8")
            return

        versions = get_torch_versions(cuda_input)
        if not versions:
            messagebox.showerror("❌ 不支持", f"暂不支持 CUDA {cuda_input} 的版本映射。\n请参考 PyTorch 官网。")
            return

        torch_ver, tv_ver, ta_ver, cuda_tag = versions
        index_url = f"https://download.pytorch.org/whl/{cuda_tag}"
        cmd = f"pip install torch=={torch_ver} torchvision=={tv_ver} torchaudio=={ta_ver} --extra-index-url {index_url}"

        result = f"""\
✅ 匹配成功！

🔧 版本信息：
   torch       : {torch_ver}
   torchvision : {tv_ver}
   torchaudio  : {ta_ver}
   CUDA 支持   : {cuda_tag.upper()}

📌 安装命令：
{cmd}
"""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state="disabled")

        self.last_command = cmd
        self.copy_btn.config(state="normal")

    def copy_command(self):
        try:
            import pyperclip
            pyperclip.copy(self.last_command)
            messagebox.showinfo("✅ 已复制", "安装命令已复制到剪贴板！")
        except ImportError:
            # 尝试使用 Tk 内置剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_command)
            self.root.update()
            messagebox.showinfo("✅ 已复制", "命令已复制到剪贴板（使用 Tk 剪贴板）！")

    def clear_all(self):
        self.cuda_entry.delete(0, tk.END)
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
        self.copy_btn.config(state="disabled")
        self.last_command = ""


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()