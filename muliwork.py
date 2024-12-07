import asyncio
import os
from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor


# API密钥列表
API_KEYS = [
    ""
]

BASE_URL = ""


# 初始化文件夹路径
WORK_DIR = Path("workmd")
OUTPUT_DIR = Path("outputmd")

initial_prompt = """
    你是一个专门从事将学术的markdown文本翻译成学术中文的AI助手并且精通数理金融。
    最重要的要求：
    0.不能省略任何内容，若全部文本翻译完，则生成提示"本次翻译任务完成"，注意一定确保全部翻译完后再回复，而不是每次都回复，绝对保证不提前生成提示。
    1. 对于markdown文档的处理，保持markdown内联latex的格式，公式块使用双美元符$$ $$，双美元符公式块需要单独成行，行内公式使用单美元符$ $。正文使用中文全角标点符号，数学文本中使用英文半角标点符号。
    2. 原markdown插入图片的代码保持原状不要作任何改动，文本中出现的HTML格式的表格转换为markdown内联表格的形式，并且保持表格中的内容不变。
    4. 原文文本中会遇到识别错乱的代码块，将其修正并
    翻译的细节要求:
    1. 英文的长句翻译通常不会直接对应中文句式，你需要作出逻辑叙述的调整。
    3. 为照顾汉语的习惯，采用一词两译的做法。例如"set"在汉语中有时译成"集合"有时译成"集"，单独使用时常译成"集合"，而在与其他词汇连用时则译成"集"（如可数集等）。
    4. 汉语"是"通常有两种含义，一是"等于"，二是"属于"。在本书中"是"只表示等于的意思，而属于的意思则用"是一个"来表示。例如，不说"X是拓扑空间"，而说"X是一个拓扑空间"。
    5. 在汉语中，长的词组常容易发生歧义。
    6. 在汉语中常难于区别单数和复数，而在英语的表达中又常常对于名词的复数形式与集合名词不加区别。对于这种情形，你需要宁可啰嗦一点，以保证不被误解。
    以下是需要翻译的内容：
    {content}
"""


async def translate_file(file_path: Path, api_key: str, semaphore: asyncio.Semaphore):
    """处理单个文件的异步函数"""
    async with semaphore:
        try:
            print(f"开始处理文件: {file_path.name}")

            client = OpenAI(
                base_url=BASE_URL,
                api_key=api_key
            )

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            output_file = OUTPUT_DIR / f"translated_{file_path.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("")

            messages = [{"role": "system", "content": initial_prompt.format(content=content)}]
            max_retries = 20
            retry_count = 0

            while True:
                try:
                    print(f"文件 {file_path.name} 发送翻译请求...")

                    with ThreadPoolExecutor() as executor:
                        response = await asyncio.get_event_loop().run_in_executor(
                            executor,
                            lambda: client.chat.completions.create(
                                model="claude-3-5-sonnet-20241022",
                                messages=messages,
                                timeout=300
                            )
                        )

                    reply = response.choices[0].message.content
                    print(f"文件 {file_path.name} 收到回复，长度：{len(reply)}")

                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(reply + "\n\n")

                    if "本次翻译任务完成" in reply:
                        print(f"文件 {file_path.name} 翻译完成")
                        break

                    messages.append({"role": "assistant", "content": reply})
                    messages.append({"role": "user",
                                     "content": "继续翻译，一次翻译尽可能多的内容，若全部文本翻译完，则生成提示'本次翻译任务完成'"})
                    retry_count = 0

                except Exception as e:
                    print(f"文件 {file_path.name} 处理出错: {str(e)}")
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"文件 {file_path.name} 超过最大重试次数")
                        return False
                    print(f"文件 {file_path.name} 重试第 {retry_count} 次...")
                    await asyncio.sleep(5)

            return True

        except Exception as e:
            print(f"文件 {file_path.name} 处理失败: {str(e)}")
            return False


async def main():
    try:
        # 创建输出目录
        OUTPUT_DIR.mkdir(exist_ok=True)

        # 获取所有markdown文件
        md_files = list(WORK_DIR.glob("*.md"))
        if not md_files:
            print("workmd文件夹中没有找到markdown文件")
            return

        print(f"找到 {len(md_files)} 个markdown文件")

        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(len(API_KEYS))

        # 创建任务列表
        tasks = []
        for i, file_path in enumerate(md_files):
            api_key = API_KEYS[i % len(API_KEYS)]
            task = translate_file(file_path, api_key, semaphore)
            tasks.append(task)

        # 等待所有翻译任务完成
        results = await asyncio.gather(*tasks)

        # 统计成功和失败的数量
        success_count = sum(1 for r in results if r)
        fail_count = len(results) - success_count

        print(f"\n翻译任务完成:")
        print(f"成功: {success_count} 个文件")
        print(f"失败: {fail_count} 个文件")

    except Exception as e:
        print(f"发生未预期的错误: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
