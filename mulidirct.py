import anthropic
import time
import random
from pathlib import Path

# Token费用计算参考值（美元/1K tokens）
INPUT_COST_PER_1K = 0.003  # $3 per million = $0.003 per 1K
OUTPUT_COST_PER_1K = 0.015  # $15 per million = $0.015 per 1K

# 初始化文件夹路径
WORK_DIR = Path("workmd")
OUTPUT_DIR = Path("outputmd")

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

# 客户端初始化
client = anthropic.Anthropic(
    api_key=""
)


class TokenCounter:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self.file_count = 0

    def add_usage(self, input_tokens, output_tokens):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.call_count += 1

    def add_file(self):
        self.file_count += 1

    def print_summary(self):
        input_cost = (self.total_input_tokens / 1000) * INPUT_COST_PER_1K
        output_cost = (self.total_output_tokens / 1000) * OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost

        print("\n=== Token 使用统计 ===")
        print(f"处理文件数: {self.file_count}")
        print(f"API调用次数: {self.call_count}")
        print(f"总输入tokens: {self.total_input_tokens:,}")
        print(f"总输出tokens: {self.total_output_tokens:,}")
        print(f"总tokens: {self.total_input_tokens + self.total_output_tokens:,}")
        print("\n=== 成本统计（美元）===")
        print(f"输入成本: ${input_cost:.4f}")
        print(f"输出成本: ${output_cost:.4f}")
        print(f"总成本: ${total_cost:.4f}")
        print(f"使用prompt caching节省成本: ${total_cost * 0.9:.4f}")
        print(f"平均每个文件成本: ${total_cost / self.file_count:.4f}")


def get_translation_prompt():
    """定义固定的翻译提示模板"""
    return """你是一个专门从事将学术的markdown文本翻译成学术中文的AI助手并且精通数学。
    最重要的要求：将全部文本翻译完后，再生成提示"本次翻译任务完成"，一定确保全部翻译完后再回复，绝对不要提前回复。
    重要的基本要求:
    1. 对于markdown文档的处理，保持markdown内联latex的格式，公式块使用双美元符$$ $$，双美元符公式块需要单独成行，行内公式使用单美元符$ $。正文使用中文全角标点符号，数学文本中使用英文半角标点符号。
    3. 你不会生成任何除了翻译内容以外的其他文本，由于我一次给你的文本很长，你可能不能通过一次回答完整，不用担心，你的单次回答被截断后，我会提示你继续。
    2. 图片的插入代码保持不变，但将文本中HTML格式的表格转换为markdown内联表格的形式，并且保持表格中的内容不变。
    翻译的细节要求:
    1. 英文的长句翻译通常不会直接对应中文句式，你需要作出逻辑叙述的调整。
    3. 为照顾汉语的习惯，采用一词两译的做法。例如"set"在汉语中有时译成"集合"有时译成"集"，单独使用时常译成"集合"，而在与其他词汇连用时则译成"集"（如可数集等）。
    4. 汉语"是"通常有两种含义，一是"等于"，二是"属于"。在本书中"是"只表示等于的意思，而属于的意思则用"是一个"来表示。例如，不说"X是拓扑空间"，而说"X是一个拓扑空间"。
    5. 在汉语中，长的词组常容易发生歧义。例如"一个可数邻域的族"可能会有以下几种理解方式：
       (1) 一个族，这个族的成员是邻域，每一个邻域是可数集。
       (2) 一个族，这个族只有一个邻域为其成员，这个邻域是可数集。
       (3) 一个族，这个族是可数的，它的每一个成员是邻域。对于不满足结合律的翻译对象是不能省掉括号的。
       遇到这种情形，你需要宁可多用几个字翻译，也尽量避免歧义的可能。
    6. 在汉语中常难于区别单数和复数，而在英语的表达中又常常对于名词的复数形式与集合名词不加区别。对于这种情形，简单地翻译可能会导致误解。因此，你需要宁可啰嗦一点，以保证不被误解。
    以下是需要翻译的内容：
    {content}"""


def get_retry_delay(retry_count):
    """计算指数退避延迟时间"""
    base_delay = 5  # 基础延迟5秒
    max_delay = 120  # 最大延迟120秒
    delay = min(base_delay * (2 ** retry_count), max_delay)
    jitter = random.uniform(0, 0.1 * delay)  # 添加随机抖动
    return delay + jitter


def translate_markdown(input_file: Path, output_file: Path, token_counter: TokenCounter):
    """翻译单个markdown文件的函数"""
    print(f"\n开始处理文件: {input_file.name}")

    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 准备输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("")

    max_retries = 20
    retry_count = 0
    accumulated_translation = ""

    while True:
        try:
            print(f"发送翻译请求...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                system=get_translation_prompt(),
                messages=[
                    {"role": "user", "content": content}
                ] if not accumulated_translation else [
                    {"role": "user", "content": content},
                    {"role": "assistant", "content": accumulated_translation},
                    {"role": "user", "content": "继续翻译剩余内容，一次尽可能多地翻译内容，避免生成其他文本"}
                ]
            )

            reply = response.content[0].text.strip()
            accumulated_translation += reply

            token_counter.add_usage(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            input_cost = (response.usage.input_tokens / 1000) * INPUT_COST_PER_1K
            output_cost = (response.usage.output_tokens / 1000) * OUTPUT_COST_PER_1K

            print(f"\n当前请求token使用:")
            print(f"输入tokens: {response.usage.input_tokens:,}")
            print(f"输出tokens: {response.usage.output_tokens:,}")
            print(f"成本: ${input_cost + output_cost:.4f}")
            print(f"收到回复，长度：{len(reply)}")

            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(reply + "\n\n")

            if "本次翻译任务完成" in reply:
                print(f"文件 {input_file.name} 翻译完成")
                token_counter.add_file()
                break

            retry_count = 0

        except anthropic.APIError as e:
            if "overloaded_error" in str(e) or "529" in str(e):
                print(f"服务器过载，等待重试...")
                retry_delay = get_retry_delay(retry_count)
                print(f"将在 {retry_delay:.1f} 秒后重试")
                time.sleep(retry_delay)
                retry_count += 1
                if retry_count > max_retries:
                    print("超过最大重试次数，任务终止。")
                    return False
                continue

            print(f"API错误: {e}")
            retry_count += 1
            if retry_count > max_retries:
                print("超过最大重试次数，任务终止。")
                return False
            retry_delay = get_retry_delay(retry_count)
            print(f"重试第 {retry_count} 次，将在 {retry_delay:.1f} 秒后重试...")
            time.sleep(retry_delay)

        except (anthropic.RateLimitError, anthropic.APIConnectionError) as e:
            print(f"连接错误或速率限制: {e}")
            retry_count += 1
            if retry_count > max_retries:
                print("超过最大重试次数，任务终止。")
                return False
            retry_delay = get_retry_delay(retry_count)
            print(f"重试第 {retry_count} 次，将在 {retry_delay:.1f} 秒后重试...")
            time.sleep(retry_delay)

        except Exception as e:
            print(f"未预期的错误: {str(e)}")
            retry_count += 1
            if retry_count > max_retries:
                print("超过最大重试次数，任务终止。")
                return False
            retry_delay = get_retry_delay(retry_count)
            print(f"重试第 {retry_count} 次，将在 {retry_delay:.1f} 秒后重试...")
            time.sleep(retry_delay)

    return True


def process_markdown_files():
    """处理文件夹中的所有markdown文件"""
    # 获取所有markdown文件
    md_files = list(WORK_DIR.glob("*.md"))
    if not md_files:
        print("workmd文件夹中没有找到markdown文件")
        return

    print(f"找到 {len(md_files)} 个markdown文件")

    # 初始化计数器
    token_counter = TokenCounter()

    # 遍历处理每个文件
    for i, input_file in enumerate(md_files, 1):
        print(f"\n=== 处理第 {i}/{len(md_files)} 个文件 ===")

        # 构建输出文件路径
        output_file = OUTPUT_DIR / f"translated_{input_file.name}"

        try:
            success = translate_markdown(input_file, output_file, token_counter)
            if not success:
                print(f"文件 {input_file.name} 处理失败")
                continue

        except Exception as e:
            print(f"处理文件 {input_file.name} 时发生错误: {e}")
            continue

    # 打印总体统计信息
    print("\n=== 批量处理完成 ===")
    token_counter.print_summary()


def main():
    try:
        # 检查工作目录是否存在
        if not WORK_DIR.exists():
            print(f"错误：工作目录 {WORK_DIR} 不存在")
            return

        process_markdown_files()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生未预期的错误: {str(e)}")


if __name__ == "__main__":
    main()
