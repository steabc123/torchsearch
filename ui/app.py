# ui/app.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
from core.cuda_detector import get_nvcc_version
from core.version_mapper import get_torch_versions
from core.command_builder import build_install_command, format_result_message, build_result_dict
from core.clipboard import copy_to_clipboard
from core.detector import get_gpu_status, get_cuda_version


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

        # 输出区（先创建按钮区域，保证按钮不会被结果区撑走）
        # 按钮区域放在输入区下面，结果区上方，保证在不同平台上可见
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill='x', pady=2, padx=20)

        self.copy_btn = tk.Button(btn_frame, text="📋 复制pip安装命令", command=self.copy_command, state="disabled", width=20)
        self.copy_btn.pack(side="left", padx=5)

        self.copy_conda_btn = tk.Button(btn_frame, text="📋 复制 Conda 命令", command=self.copy_conda_command, state="disabled", width=20)
        self.copy_conda_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="🗑 清空", command=self.clear_all, width=15)
        self.clear_btn.pack(side="left", padx=5)

        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(result_frame, text="推荐版本与安装命令:", font=("Microsoft YaHei", 10, "bold")).pack(anchor="w")

        # structured result area
        self.result_container = tk.Frame(result_frame)
        self.result_container.pack(fill="both", expand=True, pady=5)

        def make_row(label_text, parent, sticky='w'):
            row = tk.Frame(parent)
            tk.Label(row, text=label_text, width=12, anchor='w').pack(side='left')
            val = tk.Label(row, text='', anchor='w')
            val.pack(side='left', fill='x', expand=True)
            return row, val

        row, self.torch_val = make_row('torch:', self.result_container)
        row.pack(fill='x', pady=2)
        row, self.tv_val = make_row('torchvision:', self.result_container)
        row.pack(fill='x', pady=2)
        row, self.ta_val = make_row('torchaudio:', self.result_container)
        row.pack(fill='x', pady=2)
        row, self.cuda_tag_val = make_row('CUDA tag:', self.result_container)
        row.pack(fill='x', pady=2)

        # Pip command (readonly entry)
        cmd_row = tk.Frame(self.result_container)
        tk.Label(cmd_row, text='Pip 命令:', width=12, anchor='w').pack(side='left')
        self.pip_entry = tk.Entry(cmd_row, state='readonly')
        self.pip_entry.pack(side='left', fill='x', expand=True, padx=4)
        cmd_row.pack(fill='x', pady=4)

        # Conda command (readonly entry)
        conda_row = tk.Frame(self.result_container)
        tk.Label(conda_row, text='Conda 命令:', width=12, anchor='w').pack(side='left')
        self.conda_entry = tk.Entry(conda_row, state='readonly')
        self.conda_entry.pack(side='left', fill='x', expand=True, padx=4)
        conda_row.pack(fill='x', pady=4)

        # GPU info (multi-line label)
        gpu_label = tk.Label(self.result_container, text='显卡状态:', anchor='w')
        gpu_label.pack(anchor='w')
        self.gpu_text = tk.Text(self.result_container, height=4, state='disabled')
        self.gpu_text.pack(fill='both', expand=True, pady=2)

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

        pip_cmd = build_install_command(torch_ver, tv_ver, ta_ver, cuda_tag)
        conda_cmd = None
        try:
            from core.command_builder import build_conda_command
            conda_cmd = build_conda_command(torch_ver, tv_ver, ta_ver, cuda_tag)
        except Exception:
            conda_cmd = None

        # get GPU status to show to user
        gpu_info = None
        try:
            gpu_info = get_gpu_status()
        except Exception:
            gpu_info = None

        result_dict = build_result_dict(cuda_input, torch_ver, tv_ver, ta_ver, cuda_tag, pip_cmd, conda_cmd, gpu_info)

        self.display_result(result_dict)
        self.last_command = pip_cmd
        self.last_conda = conda_cmd
        self.copy_btn.config(state="normal")
        if conda_cmd:
            self.copy_conda_btn.config(state="normal")

    def is_valid_cuda_version(self, version: str) -> bool:
        return bool(re.match(r'^\d+\.\d+$', version))

    def display_result(self, text: str):
        # Accept structured dict (preferred) or legacy text
        if isinstance(text, dict):
            d = text
            self.torch_val.config(text=d.get('torch', ''))
            self.tv_val.config(text=d.get('torchvision', ''))
            self.ta_val.config(text=d.get('torchaudio', ''))
            self.cuda_tag_val.config(text=(str(d.get('pip_tag')) if d.get('pip_tag') else 'CPU/No CUDA'))

            # set pip entry
            pip_cmd = d.get('pip_cmd', '') or ''
            self.pip_entry.config(state='normal')
            self.pip_entry.delete(0, tk.END)
            self.pip_entry.insert(0, pip_cmd)
            self.pip_entry.config(state='readonly')

            # set conda entry
            conda_cmd = d.get('conda_cmd') or ''
            self.conda_entry.config(state='normal')
            self.conda_entry.delete(0, tk.END)
            self.conda_entry.insert(0, conda_cmd)
            self.conda_entry.config(state='readonly')

            # set gpu info
            gpu = d.get('gpu_info') or ''
            self.gpu_text.config(state='normal')
            self.gpu_text.delete(1.0, tk.END)
            self.gpu_text.insert(tk.END, gpu)
            self.gpu_text.config(state='disabled')
        else:
            # fallback to plain text into gpu_text area
            self.gpu_text.config(state='normal')
            self.gpu_text.delete(1.0, tk.END)
            self.gpu_text.insert(tk.END, str(text))
            self.gpu_text.config(state='disabled')

    def copy_command(self):
        # Prefer copying the current Pip entry; fallback to last_command
        cmd = ''
        try:
            cmd = self.pip_entry.get().strip()
        except Exception:
            cmd = getattr(self, 'last_command', '') or ''

        if not cmd:
            cmd = getattr(self, 'last_command', '') or ''

        if not cmd:
            messagebox.showwarning("⚠️ 空命令", "没有可复制的 Pip 命令。")
            return

        if copy_to_clipboard(cmd):
            messagebox.showinfo("✅ 已复制", "安装命令已复制到剪贴板！")
        else:
            messagebox.showerror("❌ 失败", "剪贴板操作失败，请手动复制。")

    def copy_conda_command(self):
        # Prefer copying the current Conda entry; fallback to last_conda
        cmd = ''
        try:
            cmd = self.conda_entry.get().strip()
        except Exception:
            cmd = getattr(self, 'last_conda', '') or ''

        if not cmd:
            cmd = getattr(self, 'last_conda', '') or ''

        if not cmd:
            messagebox.showwarning("⚠️ 空命令", "没有可复制的 Conda 命令。")
            return

        if copy_to_clipboard(cmd):
            messagebox.showinfo("✅ 已复制", "Conda 安装命令已复制到剪贴板！")
        else:
            messagebox.showerror("❌ 失败", "剪贴板操作失败，请手动复制。")

    def clear_all(self):
        self.cuda_entry.delete(0, tk.END)
        # clear structured fields
        self.torch_val.config(text='')
        self.tv_val.config(text='')
        self.ta_val.config(text='')
        self.cuda_tag_val.config(text='')
        self.pip_entry.config(state='normal')
        self.pip_entry.delete(0, tk.END)
        self.pip_entry.config(state='readonly')
        self.conda_entry.config(state='normal')
        self.conda_entry.delete(0, tk.END)
        self.conda_entry.config(state='readonly')
        self.gpu_text.config(state='normal')
        self.gpu_text.delete(1.0, tk.END)
        self.gpu_text.config(state='disabled')
        self.copy_btn.config(state="disabled")
        self.copy_conda_btn.config(state="disabled")
        self.last_command = ""
        self.last_conda = None
