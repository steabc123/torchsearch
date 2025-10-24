def build_install_command(torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None):
    """Build a pip install command. If cuda_tag is falsy, omit the index URL.

    Accepts cuda_tag like 'cu118' or None.
    """
    parts = [f"torch=={torch_ver}", f"torchvision=={tv_ver}", f"torchaudio=={ta_ver}"]
    # remove any None parts (in case some packages are unavailable)
    parts = [p for p in parts if 'None' not in p]

    if cuda_tag:
        index_url = f"https://download.pytorch.org/whl/{cuda_tag}"
        cmd = f"pip install {' '.join(parts)} --extra-index-url {index_url}"
    else:
        cmd = f"pip install {' '.join(parts)}"
    return cmd

def format_result_message(cuda_version: str, torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None, cmd: str):
    cuda_display = (str(cuda_tag).upper() if cuda_tag else 'CPU/No CUDA index')
    return f"""
✅ 匹配成功！

🔧 版本信息：
   torch       : {torch_ver}
   torchvision : {tv_ver}
   torchaudio  : {ta_ver}
   CUDA 支持   : {cuda_display}

📌 安装命令：
{cmd}
"""