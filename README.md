# 并行大模型学术Markdown翻译工具

一个基于大模型的多线程学术文档翻译工具，专门用于处理包含复杂数学公式的markdown文本。

## 🌟 特点

- 支持复杂的数学公式和LaTeX格式
- 智能处理章节连贯性
- 多API并行处理，提高翻译效率
- 完整的后处理工具链
- 支持流式和非流式翻译模式

## 📁 项目结构

```
.
├── muliwork.py       # 中转API非流式任务处理
├── streaming.py      # 中转API流式任务处理
├── mulidirct.py      # 直连API任务处理
├── 后处理模块/
│   ├── repro.py           # 特殊字符处理修复
│   ├── image.py           # 图片插入样式统一
│   ├── dollar_checker.py  # LaTeX公式符号检查
│   ├── commd.py           # Markdown文件合并
│   ├── inputimages/       # 图片输入目录
│   ├── outputimages/      # 图片输出目录
│   ├── pending/          # 待处理文件目录
│   └── reprocessing/     # 重处理文件目录
├── workmd/           # 待翻译文件目录
└── outputmd/         # 翻译结果输出目录
```

## 🚀 核心功能

### 1. 翻译处理
- **章节级翻译**：每次处理一个完整章节，确保上下文连贯性
- **公式处理**：大模型可以精确处理LaTeX数学公式，保持格式完整性

### 2. 并行处理
- 支持多个API密钥同时工作
- 自动负载均衡
- 错误重试机制

### 3. 后处理工具链
- **repro.py**: 修复特殊字符渲染问题
- **image.py**: 统一图片插入格式
- **dollar_checker.py**: 检查LaTeX公式符号配对
- **commd.py**: 合并处理后的markdown文件

## 💻 使用方法

1. **环境准备**
   ```bash
   pip install openai anthropic asyncio
   ```

2. **配置API密钥**
   - 在相应的Python文件中配置你的API密钥：
     ```python
     API_KEYS = [
         "your-api-key-1",
         "your-api-key-2"
     ]
     ```

3. **文件准备**
   - 将待翻译的markdown文件放入`workmd`目录
   - 确保图片文件已放入`inputimages`目录

4. **运行翻译**
   ```bash
   # 使用中转API非流式处理
   python muliwork.py
   
   # 或使用直连API处理
   python mulidirct.py
   ```

5. **后处理**
   ```bash
   # 修复特殊字符
   python repro.py
   
   # 处理图片格式
   python image.py
   
   # 检查LaTeX公式
   python dollar_checker.py
   
   # 合并文件
   python commd.py
   ```

## ⚡ 性能优化建议

1. 根据文件大小调整并行数量
2. 合理配置重试参数
3. 监控API使用量，避免超限
4. 定期检查输出文件质量

## 🔧 故障排除

1. **API错误**
   - 检查API密钥是否有效
   - 确认API额度是否充足
   - 检查网络连接状态
2. **文件处理错误**
   - 确保文件权限正确
   - 验证文件格式完整性
3. **LaTeX渲染问题**
   - 运行`dollar_checker.py`检查符号配对
   - 验证公式格式完整性

## 📝 注意事项

- 定期备份重要文档
- 监控API使用量和成本
- 检查输出文件的翻译质量
- 注意保护API密钥安全

## 📋 项目信息

- **创建日期**: 2024-12-7
- **创建和维护**: Liu Jingkang
- **联系方式**: jkl200407@gmail.com

## 🤝 贡献指南

欢迎提交问题和改进建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建你的特性分支
3. 提交你的改动
4. 推送到你的分支
5. 创建一个Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。