import re
import subprocess
import sys


def get_nvcc_version():
    """尝试通过运行 nvcc --version 获取 CUDA 版本"""
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, check=True)
        output = result.stdout
        # 匹配版本号，如 "Cuda compilation tools, release 11.8, V11.8.89"
        match = re.search(r'release (\d+\.\d+)', output)
        if match:
            return match.group(1)
        else:
            print("无法从 nvcc 输出中解析 CUDA 版本。")
            return None
    except FileNotFoundError:
        print("未找到 nvcc。请确认 CUDA 工具包已安装且 nvcc 在 PATH 中。")
        return None
    except subprocess.CalledProcessError:
        print("运行 nvcc --version 时出错。")
        return None


def get_torch_versions(cuda_version):
    """根据 CUDA 版本返回推荐的 torch、torchvision、torchaudio 版本"""
    # 映射 CUDA 版本到 PyTorch 预编译版本
    # 格式: {cuda_version: (torch_version, torchvision_version, torchaudio_version, extra_index_url)}
    # 使用 PyTorch 官方发布的 wheel 链接
    version_map = {
        '10.2': ('1.13.1', '0.14.1', '0.13.1', 'https://download.pytorch.org/whl/cu102'),
        '11.3': ('1.13.1', '0.14.1', '0.13.1', 'https://download.pytorch.org/whl/cu113'),
        '11.6': ('1.13.1', '0.14.1', '0.13.1', 'https://download.pytorch.org/whl/cu116'),
        '11.7': ('2.0.1', '0.15.2', '0.15.1', 'https://download.pytorch.org/whl/cu117'),
        '11.8': ('2.1.2', '0.16.2', '2.1.2', 'https://download.pytorch.org/whl/cu118'),
        '12.1': ('2.2.2', '0.17.2', '2.2.2', 'https://download.pytorch.org/whl/cu121'),
        '12.4': ('2.3.1', '0.18.1', '2.3.1', 'https://download.pytorch.org/whl/cu121'),  # 注意：2.3+ 使用 cu121 兼容 12.4
    }

    # 官方有时会用 cu118 支持 11.8，cu121 支持 12.1+
    # 对输入做模糊匹配（比如 11.x -> 找最接近的）
    cuda_key = None
    if cuda_version in version_map:
        cuda_key = cuda_version
    else:
        # 尝试匹配主版本（如 11.x -> 11.8）
        major = cuda_version.split('.')[0]
        fallback = {
            '11': '11.8',
            '12': '12.1'
        }
        if major in fallback and fallback[major] in version_map:
            cuda_key = fallback[major]
            print(f"⚠️ 未精确支持 CUDA {cuda_version}，将使用兼容版本 {cuda_key} 的 PyTorch。")

    if not cuda_key:
        return None

    return version_map[cuda_key]


def main():
    print("🔍 PyTorch CUDA 版本适配助手")
    print("请选择输入方式：")
    print("1. 手动输入 CUDA 版本（如 11.8）")
    print("2. 自动检测 nvcc 版本")

    choice = input("请输入选择 (1/2): ").strip()

    if choice == '2':
        cuda_ver = get_nvcc_version()
        if not cuda_ver:
            print("无法获取 nvcc 版本，退出。")
            return
        print(f"✅ 检测到 CUDA 版本: {cuda_ver}")
    elif choice == '1':
        cuda_ver = input("请输入你的 CUDA 版本（如 11.8）: ").strip()
        # 简单验证格式
        if not re.match(r'^\d+\.\d+$', cuda_ver):
            print("❌ CUDA 版本格式错误，请输入如 11.8 的版本号。")
            return
    else:
        print("❌ 无效选择。")
        return

    # 获取推荐版本
    versions = get_torch_versions(cuda_ver)
    if not versions:
        print(f"❌ 暂不支持 CUDA {cuda_ver} 的 PyTorch 版本映射。")
        print("请参考官方安装页面：https://pytorch.org/get-started/locally/")
        return

    torch_ver, tv_ver, ta_ver, index_url = versions

    print("\n✅ 推荐安装版本：")
    print(f"   torch         : {torch_ver}")
    print(f"   torchvision   : {tv_ver}")
    print(f"   torchaudio    : {ta_ver}")
    print(f"   CUDA 支持     : {index_url.split('/')[-1]}")

    print(f"\npip 安装命令：")
    cmd = f"pip install torch=={torch_ver} torchvision=={tv_ver} torchaudio=={ta_ver} --extra-index-url {index_url}"
    print(cmd)

    # 提示用户复制命令
    copy_cmd = input("\n是否复制安装命令到剪贴板？(y/n): ").strip().lower()
    if copy_cmd in ('y', 'yes'):
        try:
            import pyperclip
            pyperclip.copy(cmd)
            print("✅ 命令已复制到剪贴板！")
        except ImportError:
            print("❌ 未安装 pyperclip，无法复制。请运行: pip install pyperclip")


if __name__ == '__main__':
    main()