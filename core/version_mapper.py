from utils.constants import TORCH_VERSION_MAP

def get_torch_versions(cuda_version: str):
    # 精确匹配
    if cuda_version in TORCH_VERSION_MAP:
        return TORCH_VERSION_MAP[cuda_version]

    # 按主版本 fallback
    major = cuda_version.split('.')[0]
    fallback_map = {'11': '11.8', '12': '12.1'}
    if major in fallback_map:
        fallback_ver = fallback_map[major]
        return TORCH_VERSION_MAP.get(fallback_ver)
    return None