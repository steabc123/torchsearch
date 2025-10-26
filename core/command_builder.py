def build_install_command(torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None):
    """Build a pip install command. If cuda_tag is falsy, omit the index URL.

    Accepts cuda_tag like 'cu118' or None.
    """
    parts = [f"torch=={torch_ver}", f"torchvision=={tv_ver}", f"torchaudio=={ta_ver}"]
    # remove any None parts (in case some packages are unavailable)
    parts = [p for p in parts if 'None' not in p]

    if cuda_tag:
        # ensure we don't accidentally print the literal placeholder
        index_url = f"https://download.pytorch.org/whl/{cuda_tag}"
        cmd = f"pip install {' '.join(parts)} --extra-index-url {index_url}"
    else:
        cmd = f"pip install {' '.join(parts)}"
    return cmd


def build_conda_command(torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None):
    """Build a simple conda install command.

    For CUDA-enabled builds we add a matching cudatoolkit spec and recommend channels.
    This is a pragmatic, minimal command that should work in most common setups.
    """
    parts = [f"pytorch=={torch_ver}", f"torchvision=={tv_ver}", f"torchaudio=={ta_ver}"]
    parts = [p for p in parts if 'None' not in p]

    # conda package names are slightly different (pytorch instead of torch)
    base = f"conda install {' '.join(parts)} -c pytorch"

    if cuda_tag and isinstance(cuda_tag, str) and cuda_tag.startswith('cu'):
        # map cu118 -> 11.8
        try:
            ver = cuda_tag[2:]
            # insert a dot: '118' -> '11.8' or '117'->'11.7', handle common lengths
            if len(ver) == 3:
                cudatoolkit = f"{ver[0:2]}.{ver[2]}"
            elif len(ver) == 4:
                cudatoolkit = f"{ver[0:2]}.{ver[2:]}"
            else:
                # fallback, try to interpret as major.minor already
                cudatoolkit = ver
            base += f" cudatoolkit={cudatoolkit} -c nvidia"
        except Exception:
            # if mapping fails, just recommend channels
            base += " -c nvidia"
    return base


def build_result_dict(cuda_version: str, torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None, pip_cmd: str, conda_cmd: str | None = None, gpu_info: str | None = None) -> dict:
    """Return a structured dict representing the result suitable for UI rendering.

    This keeps presentation data separated from textual formatting.
    """
    return {
        "cuda_input": cuda_version,
        "torch": torch_ver,
        "torchvision": tv_ver,
        "torchaudio": ta_ver,
        "pip_tag": cuda_tag,
        "pip_cmd": pip_cmd,
        "conda_cmd": conda_cmd,
        "gpu_info": gpu_info,
    }


def format_result_message(cuda_version: str, torch_ver: str, tv_ver: str, ta_ver: str, cuda_tag: str | None, pip_cmd: str, conda_cmd: str | None = None, gpu_info: str | None = None):
    cuda_display = (str(cuda_tag).upper() if cuda_tag else 'CPU/No CUDA index')
    gpu_section = f"\n\n显卡状态:\n{gpu_info}\n" if gpu_info else ""
    conda_block = f"\n\nConda 安装命令：\n{conda_cmd}" if conda_cmd else ""
    return f"""
✅ 匹配成功！

🔧 版本信息：
   torch       : {torch_ver}
   torchvision : {tv_ver}
   torchaudio  : {ta_ver}
   CUDA 支持   : {cuda_display}{gpu_section}

📌 Pip 安装命令：
{pip_cmd}{conda_block}
"""