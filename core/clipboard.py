def copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # 回退到 Tk 原生剪贴板
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            return False