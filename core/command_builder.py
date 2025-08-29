def build_install_command(torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str):
    index_url = f"https://download.pytorch.org/whl/{cuda_tag}"
    cmd = f"pip install torch=={torch_ver} torchvision=={tv_ver} torchaudio=={ta_ver} --extra-index-url {index_url}"
    return cmd

def format_result_message(cuda_version: str, torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str, cmd: str):
    return f"""
✅ 匹配成功！

🔧 版本信息：
   torch       : {torch_ver}
   torchvision : {tv_ver}
   torchaudio  : {ta_ver}
   CUDA 支持   : {cuda_tag.upper()}

📌 安装命令：
{cmd}
"""