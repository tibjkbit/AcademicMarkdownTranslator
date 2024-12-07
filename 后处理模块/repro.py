import os
import re
import ast  # 引入ast模块，用于安全地还原repr格式

def process_markdown_text(content):
    """
    处理Markdown文本，规范化换行符和数学公式

    Args:
        content (str): 输入的Markdown文本

    Returns:
        str: 处理后的文本
    """
    # 将内容转换为repr格式
    repr_content = repr(content)

    formulas = []

    def save_formula(match):
        formulas.append(match.group(0))
        return f"###FORMULA###" + str(len(formulas) - 1) + "###"

    # 保存所有数学公式（包括单个$和双个$$的情况）
    pattern = r'\$\$[^$]+\$\$|\$[^$]+\$'
    protected_text = re.sub(pattern, save_formula, repr_content)

    # 处理非公式文本中的单个\\n，注意要忽略|\\n|的情况
    # 首先匹配|\\n|这种情况并暂时替换为特殊标记
    protected_text = re.sub(r'\|\\n\|', r'###PIPE_N###', protected_text)

    # 然后处理所有的\\n，替换成\\n\\n
    protected_text = re.sub(r'(?<!\\n)\\n(?!\\n)', r'\\n\\n', protected_text)

    # 恢复|\\n|为原样
    protected_text = protected_text.replace('###PIPE_N###', r'|\n|')


    def process_formula(formula):
        # 处理公式中的特定字符
        formula = re.sub(r'ightbrack', r'ight\\\\rbrack', formula)
        formula = re.sub(r'(?<![rR])(ight)', r'\\\\right', formula)
        formula = re.sub(r'(?<!n)abla(?![a-zA-Z])', r'\\\\nabla', formula)
        return formula

    def restore_formula(match):
        formula_str = match.group(0)
        index = int(formula_str.split('###')[2])
        formula = formulas[index]
        return process_formula(formula)

    # 恢复处理后的公式
    final_repr_text = re.sub(r'###FORMULA###\d+###', restore_formula, protected_text)

    final_text = ast.literal_eval(final_repr_text)  # 安全还原为普通文本
    # 确保恢复后的文本中的换行符正确显示
    return final_text


def process_markdown_files_in_directory(directory_path):
    """
    遍历指定目录中的所有Markdown文件并处理它们

    Args:
        directory_path (str): 目标文件夹路径
    """
    # 遍历文件夹中的所有Markdown文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # 仅处理Markdown文件（扩展名为.md）
        if os.path.isfile(file_path) and filename.endswith('.md'):
            print(f"正在处理文件: {filename}")
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 处理文件内容
            processed_content = process_markdown_text(content)

            # 覆写原文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(processed_content)
            print(f"文件 {filename} 处理完成。\n")


# 主程序入口
if __name__ == "__main__":
    directory_path = ("pending")
    process_markdown_files_in_directory(directory_path)
