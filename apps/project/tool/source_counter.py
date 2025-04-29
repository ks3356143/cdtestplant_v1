import lizard
import os
import zipfile
from pathlib import Path

def analyze_code_directory(file_path):
    results = {
        'comment_rate': 0.0,  # 注释率-手动
        'total_lines': 0,  # 总函数
        'effective_lines': 0,  # 有效代码行数
        'avg_function_lines': 0,  # 平均模块行数
        'avg_cyclomatic': 0,  # 平均圈复杂度
        'avg_fan_out': 0,  # 平均扇出
        'function_count': 0  # 函数个数
    }
    total_comments = 0
    total_blanks = 0
    total_lines = 0
    total_effective = 0
    functions = []
    for root, _, files in os.walk(file_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.h', '.hpp', '.cc', '.cxx')):
                filepath = os.path.join(root, file)
                # 使用 lizard 分析代码结构
                analysis = lizard.analyze_file(filepath)
                functions.extend(analysis.function_list)
                # 使用 lizard 的有效代码行数统计
                total_effective += analysis.nloc
                # 手动统计注释行数（新方法）
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.readlines()
                    total_comments += sum(
                        1 for line in content if line.strip().startswith(('//', '/*', '*')) or '*/' in line)
                    total_blanks += sum(1 for line in content if not line.strip())
    # 计算函数相关指标
    if functions:
        cyclomatic_list = [f.cyclomatic_complexity for f in functions]
        high_cyclo = sum(1 for c in cyclomatic_list if c >= 20)
        # 输出的指标
        results['function_count'] = len(functions)  # 模块数量
        results['avg_function_lines'] = sum(f.length for f in functions) / len(functions)  # 平均规模
        results['avg_cyclomatic'] = sum(f.cyclomatic_complexity for f in functions) / len(functions)  # 平均圈复杂
        results['avg_fan_out'] = sum(f.fan_out for f in functions) / len(functions)  # 平均扇出
        results['max_cyclomatic'] = max(cyclomatic_list)  # 模块最大圈复杂度
        results['high_cyclomatic_ratio'] = high_cyclo / len(functions) * 100  # 圈复杂度>20比例
        total_lines = sum(f.length for f in functions)

    # 计算全局指标 - 输出
    if total_lines > 0:
        results['comment_lines'] = total_comments if total_comments > 0 else 0
        results['comment_rate'] = total_comments / total_lines * 100 if total_comments > 0 else 0
        results['total_lines'] = total_lines
        results['effective_lines'] = total_effective
        results['total_blanks'] = total_blanks
        results['code_ratio'] = total_effective / total_lines if total_lines > 0 else 0
    return results

# 解压zip文件方法
def extract_and_get_paths(zip_path: str,
                          extract_to: str = 'unzipped_files') -> str:
    """
    解压ZIP文件并返回目标扩展名文件的绝对路径列表
    参数:
        zip_path: ZIP文件路径
        extract_to: 解压目录(默认'unzipped_files')
        target_extensions: 目标文件扩展名(默认('.c', '.h'))

    返回:
        匹配文件的绝对路径列表
    """
    # 创建解压目录(如果不存在)
    if extract_to is None:
        extract_to = os.path.join(os.getcwd(), f"unzip_temp_{os.urandom(4).hex()}")
    os.makedirs(extract_to, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            return os.path.abspath(extract_to)
    except zipfile.BadZipFile:
        raise ValueError(f"无效的ZIP文件: {zip_path}")
    except Exception as e:
        raise RuntimeError(f"解压失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    path = Path("../Cpro/")
    if not path.is_dir():
        print("错误: 路径不存在或不是目录")
    else:
        stats = analyze_code_directory(path)

        print("\n代码分析结果:")
        print(f"1. 注释率: {stats['comment_rate']:.2f}%")
        print(
            f"2. 有效代码行数/总行数: {stats['total_lines']}/{stats['effective_lines']} (比例: {stats['code_ratio']:.2f})")
        print(f"3. 函数数量: {stats['function_count']}")
        print(f"4. 函数平均行数: {stats['avg_function_lines']:.1f}")
        print(f"5. 函数平均圈复杂度: {stats['avg_cyclomatic']:.1f}")
        print(f"6. 函数平均扇出数: {stats['avg_fan_out']:.1f}")
