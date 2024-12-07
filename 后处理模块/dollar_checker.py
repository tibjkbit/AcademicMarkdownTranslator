# dollar_checker.py
import os
from pathlib import Path
import shutil


class DollarChecker:
    def __init__(self, input_dir: str, passed_dir: str, failed_dir: str):
        self.input_dir = Path(input_dir)
        self.passed_dir = Path(passed_dir)
        self.failed_dir = Path(failed_dir)

        # 创建必要的文件夹
        self.passed_dir.mkdir(exist_ok=True)
        self.failed_dir.mkdir(exist_ok=True)

    def check_dollar_signs(self, content: str) -> bool:
        """检查文本中 $$ 和 $ 的个数是否都是偶数"""
        double_dollars = content.count('$$')
        single_dollars = content.count('$') - (2 * double_dollars)
        return double_dollars % 2 == 0 and single_dollars % 2 == 0

    def process_directory(self):
        """处理指定目录下的所有markdown文件"""
        print(f"\n开始检查文件夹 {self.input_dir} 中的文件...")

        for filename in os.listdir(self.input_dir):
            if not filename.endswith('.md'):
                continue

            file_path = self.input_dir / filename
            print(f"检查文件: {filename}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if self.check_dollar_signs(content):
                    shutil.copy2(file_path, self.passed_dir / filename)
                    print(f"文件 {filename} 检查通过，已复制到 {self.passed_dir}")
                else:
                    shutil.move(file_path, self.failed_dir / filename)
                    print(f"文件 {filename} 检查未通过，已移动到 {self.failed_dir}")

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")


if __name__ == "__main__":
    checker = DollarChecker("outputmd", "reprocessing", "pending")
    checker.process_directory()
