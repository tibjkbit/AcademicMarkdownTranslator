import os
from pathlib import Path


def merge_markdown_files(folder_path, output_file='merged_output.md'):
    """
    将指定文件夹下的所有markdown文件按文件名排序合并

    Args:
        folder_path (str): markdown文件所在的文件夹路径
        output_file (str): 输出文件名，默认为'merged_output.md'
    """
    # 确保文件夹路径存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹 '{folder_path}' 不存在")

    # 获取所有markdown文件
    markdown_files = []
    for file in Path(folder_path).glob('*.md'):
        markdown_files.append(str(file))

    # 按文件名排序
    markdown_files.sort()

    if not markdown_files:
        print(f"在 '{folder_path}' 中没有找到markdown文件")
        return

    # 合并文件内容
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, md_file in enumerate(markdown_files):
            print(f"正在处理: {md_file}")

            # 读取文件内容
            with open(md_file, 'r', encoding='utf-8') as infile:
                content = infile.read()

            # 写入分隔符（除了第一个文件）
            if i > 0:
                outfile.write('\n\n---\n\n')

            # 写入文件内容
            outfile.write(content)

    print(f"\n合并完成！输出文件: {output_file}")
    print(f"共处理了 {len(markdown_files)} 个markdown文件")


# 使用示例
if __name__ == '__main__':
    # 替换为你的文件夹路径
    folder_path = r''
    merge_markdown_files(folder_path)
