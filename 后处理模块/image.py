import os
import re

# 设置输入输出目录
input_folder = './inputimages'  # 输入文件夹，包含所有的markdown文件
output_folder = './outputimages'  # 输出文件夹，保存修改后的markdown文件

# 创建output文件夹（如果不存在的话）
os.makedirs(output_folder, exist_ok=True)

# 正则表达式，匹配markdown中的图片语法
image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


# 用于处理和替换路径的函数
def modify_image_path(image_path):
    # 如果是绝对路径（或包含`:/`），直接提取文件名部分
    if os.path.isabs(image_path) or image_path.startswith("D:/") or image_path.startswith("C:/"):
        filename = os.path.basename(image_path)
    # 如果是相对路径，则直接使用
    else:
        filename = os.path.basename(image_path)

    # 返回修改后的路径，统一指向"./images/"目录
    return f'./images/{filename}'


# 处理一个markdown文件的函数
def process_markdown_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换所有图片路径为HTML img标签，并加入缩放样式
    def replace_image(match):
        alt_text = match.group(1)  # 获取图片的alt文本
        image_path = match.group(2)  # 获取图片的路径
        new_path = modify_image_path(image_path)
        # 返回HTML格式的img标签，并添加缩放样式
        return f'<img src="{new_path}" alt="{alt_text}" style="zoom:50%;" />'

    # 使用正则表达式替换图片路径
    modified_content = re.sub(image_pattern, replace_image, content)

    # 将修改后的内容写入到输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)


if __name__ == "__main__":
    # 遍历输入文件夹中的所有markdown文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.md'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # 处理每个markdown文件
            process_markdown_file(input_file_path, output_file_path)
            print(f'Processed {filename}')

    print("All files processed successfully!")
