# ui/app.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
from core.cuda_detector import get_nvcc_version
from core.version_mapper import get_torch_versions
from core.command_builder import build_install_command, format_result_message
from core.clipboard import copy_to_clipboard


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 PyTorch CUDA 版本选择助手")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.last_command = ""

        self.setup_ui()

    def setup_ui(self):
        # 标题
        title = tk.Label(self.root, text="PyTorch CUDA 版本适配器", font=("Microsoft YaHei", 16, "bold"))
        title.pack(pady=10)

        desc = tk.Label(self.root, text="选择 CUDA 版本，获取对应的 torch 安装命令", font=("Microsoft YaHei", 10))
        desc.pack(pady=5)

        # 输入区
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=20, fill="x")

        tk.Label(frame, text="CUDA 版本:", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.cuda_entry = tk.Entry(frame, width=20, font=("Courier", 12))
        self.cuda_entry.grid(row=0, column=1, padx=5, pady=5)

        self.auto_btn = tk.Button(frame, text="🔍 自动检测 nvcc", command=self.auto_detect, width=15)
        self.auto_btn.grid(row=0, column=2, padx=5)

        self.go_btn = tk.Button(frame, text="🚀 开始匹配", command=self.run_match, width=15)
        self.go_btn.grid(row=1, column=2, pady=10)

        # 输出区
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(result_frame, text="推荐版本与安装命令:", font=("Microsoft YaHei", 10, "bold")).pack(anchor="w")

        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, font=("Courier", 10), state="disabled")
        self.result_text.pack(fill="both", expand=True, pady=5)

        # 按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        self.copy_btn = tk.Button(btn_frame, text="📋 复制安装命令", command=self.copy_command, state="disabled", width=20)
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="🗑 清空", command=self.clear_all, width=15)
        self.clear_btn.pack(side="left", padx=5)

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
        if not self.is_valid_cuda_version(cuda_input):
            messagebox.showerror("❌ 错误", "请输入有效的 CUDA 版本，如 11.8")
            return

        versions = get_torch_versions(cuda_input)
        if not versions:
            messagebox.showerror("❌ 不支持", f"暂不支持 CUDA {cuda_input} 的版本映射。\n请参考 PyTorch 官网。")
            return

        # Support both old tuple return (torch_ver, tv_ver, ta_ver, cuda_tag)
        # and new dict-based return {"torch":..., "torchvision":..., "torchaudio":..., "pip_tag":...}
        if isinstance(versions, dict):
            torch_ver = versions.get("torch")
            tv_ver = versions.get("torchvision")
            ta_ver = versions.get("torchaudio")
            cuda_tag = versions.get("pip_tag")
        else:
            try:
                torch_ver, tv_ver, ta_ver, cuda_tag = versions
            except Exception:
                messagebox.showerror("❌ 错误", "版本映射格式不正确。")
                return

        # Validate extracted values
        if not (torch_ver and (tv_ver is not None) and (ta_ver is not None)):
            messagebox.showerror("❌ 不支持", "未能从映射中获取完整的版本信息。")
            return

        cmd = build_install_command(torch_ver, tv_ver, ta_ver, cuda_tag)
        result_msg = format_result_message(cuda_input, torch_ver, tv_ver, ta_ver, cuda_tag, cmd)

        self.display_result(result_msg)
        self.last_command = cmd
        self.copy_btn.config(state="normal")

    def is_valid_cuda_version(self, version: str) -> bool:
        return bool(re.match(r'^\d+\.\d+$', version))

    def display_result(self, text: str):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")

    def copy_command(self):
        if not self.last_command:
            return
        if copy_to_clipboard(self.last_command):
            messagebox.showinfo("✅ 已复制", "安装命令已复制到剪贴板！")
        else:
            messagebox.showerror("❌ 失败", "剪贴板操作失败，请手动复制。")

    def clear_all(self):
        self.cuda_entry.delete(0, tk.END)
        self.display_result("")
        self.copy_btn.config(state="disabled")
        self.last_command = ""
