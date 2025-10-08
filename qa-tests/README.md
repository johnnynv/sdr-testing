# RAG 系统 UI 自动化测试

基于 **Playwright + Xvfb** 的端到端自动化测试套件，用于测试 NVIDIA Streaming Data to RAG 系统。

## 🎯 技术栈

- **Playwright**: 浏览器自动化框架
- **Xvfb**: X Virtual Framebuffer (虚拟显示服务器)
- **Python 3.8+**: 测试脚本语言

## ✨ 特性

- ✅ 真实浏览器环境测试（非 headless）
- ✅ 自动截图功能（每个查询都截图）
- ✅ 无需真实显示器（使用 Xvfb 虚拟显示）
- ✅ 完整的错误处理和报告
- ✅ JSON 格式测试报告

---

## 📋 测试内容

### 1. 时间过滤功能测试 (`test_rag_time_filtering.py`)
- ✅ 相对时间查询（最近 N 分钟/小时）
- ✅ 时间窗口查询（N 分钟前）
- ✅ 排除最近内容查询
- ✅ 边界条件测试
- ✅ 错误处理测试

**测试数量**: 19 个测试用例

### 2. 错误处理与智能提示测试 (`test_rag_error_handling.py`)
- ✅ 缺少通道号处理
- ✅ 缺少时间信息处理
- ✅ 格式错误自动纠正
- ✅ 无效值错误提示
- ✅ 极度模糊查询引导

**测试数量**: 19 个测试用例

---

## 🚀 快速开始

### 前提条件

```bash
# 1. Python 3.8+
python3 --version

# 2. 前端服务运行
curl http://localhost:3000

# 3. Xvfb 已安装
xvfb-run --help
```

### 一键运行（推荐）

```bash
cd /localhome/keystone/jupyter_workspace/sdr-testing/qa-tests

# 激活虚拟环境
source venv/bin/activate

# 运行统一启动器（交互式菜单）
python3 run_all_tests.py
```

### 手动运行单个测试

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 运行时间过滤测试
xvfb-run -a --server-args="-screen 0 1920x1080x24" python3 test_rag_time_filtering.py

# 3. 运行错误处理测试
xvfb-run -a --server-args="-screen 0 1920x1080x24" python3 test_rag_error_handling.py
```

### 快速测试单个查询

```bash
source venv/bin/activate

# 使用默认查询
xvfb-run python3 quick_test.py

# 自定义查询
xvfb-run python3 quick_test.py "Summarize channel 0 from the last 5 minutes"
```

---

## 🖼️ 截图功能

### 自动截图

所有测试查询都会自动截图，保存在 `screenshots/` 目录：

```
screenshots/
├── query_20251008_120001.png         # 时间过滤测试截图
├── query_20251008_120002.png
├── error_query_20251008_120030.png   # 错误处理测试截图
└── quick_test_20251008_120100.png    # 快速测试截图
```

### 截图特点

- 📸 **全页面截图** (`full_page=True`)
- 🎨 **1920x1080 分辨率** (Xvfb 虚拟显示)
- ⏱️ **带时间戳命名**
- 💾 **PNG 格式，高质量**

### 查看截图

```bash
# 列出所有截图
ls -lht screenshots/*.png

# 最新的 10 张截图
ls -lht screenshots/*.png | head -10

# 打开最新截图（如果有图形环境）
xdg-open screenshots/$(ls -t screenshots/ | head -1)
```

---

## 📊 测试报告

### 报告格式

测试完成后生成 JSON 格式报告：

```json
{
  "timestamp": "2025-10-08T12:00:00+00:00",
  "total": 19,
  "success": 17,
  "failed": 2,
  "avg_response_time_ms": 2341,
  "results": [...]
}
```

### 查看报告

```bash
# 列出所有报告
ls -lht *_report_*.json

# 查看最新报告（美化输出）
cat $(ls -t *_report_*.json | head -1) | jq .
```

---

## 🔧 配置选项

### Xvfb 参数

```bash
# 默认配置：1920x1080, 24位色深
xvfb-run -a --server-args="-screen 0 1920x1080x24" python3 test.py

# 高分辨率
xvfb-run -a --server-args="-screen 0 2560x1440x24" python3 test.py

# 多显示器
xvfb-run -a --server-args="-screen 0 1920x1080x24 -screen 1 1920x1080x24" python3 test.py
```

### 禁用截图

编辑测试文件：

```python
# 时间过滤测试
tester = RAGTimeFilterTester(headless=False, enable_screenshots=False)

# 错误处理测试
tester = RAGErrorHandlingTester(headless=False, enable_screenshots=False)
```

### 调整等待时间

如果系统响应慢，可以增加等待时间：

```python
# 在 execute_query 方法中
page.wait_for_timeout(2000)  # 改为 5000 (5秒)
```

---

## 🎯 测试标准

### 时间过滤功能
- ✅ 80%+ 测试通过率
- ✅ 平均响应时间 < 5秒
- ✅ 所有测试有截图证据

### 错误处理
- ✅ 90%+ 查询得到响应
- ✅ 80%+ 响应有帮助（包含建议/示例）
- ✅ 平均响应时间 < 5秒
- ✅ 所有测试有截图证据

---

## 🛠️ 故障排查

### Xvfb 相关

```bash
# 检查 Xvfb 是否安装
which xvfb-run
# 如果未安装: sudo apt-get install xvfb

# 检查 Xvfb 进程
ps aux | grep Xvfb

# 手动启动 Xvfb（调试用）
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
python3 test_rag_time_filtering.py
```

### Playwright 错误

```bash
# 重新安装浏览器
source venv/bin/activate
playwright install chromium

# 测试 Playwright
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### 前端连接问题

```bash
# 检查前端服务
curl -I http://localhost:3000

# 检查 Docker 容器
docker ps | grep -E "ui|agentiq"

# 检查端口占用
netstat -tuln | grep 3000
```

### 截图失败

```bash
# 检查目录权限
ls -ld screenshots/

# 手动创建目录
mkdir -p screenshots
chmod 755 screenshots

# 检查磁盘空间
df -h .
```

---

## 📁 文件结构

```
qa-tests/
├── run_all_tests.py                 # 统一启动器 🎬 ⭐
├── test_rag_time_filtering.py      # 时间过滤功能测试
├── test_rag_error_handling.py      # 错误处理测试
├── quick_test.py                    # 快速单查询测试 🚀
├── README.md                        # 本文档 📖
├── venv/                            # Python 虚拟环境
├── screenshots/                     # 截图目录 📸
├── *.json                           # 测试报告 📊
├── rag_time_filter_tests.md        # 测试用例文档
└── rag_query_error_handling_tests.md  # 错误处理文档
```

---

## 💡 使用技巧

### 1. 快速验证单个功能

```bash
source venv/bin/activate
python3 run_all_tests.py  # 选择选项 4 - 快速测试

# 或直接运行
xvfb-run python3 quick_test.py "your test query"
```

### 2. 批量运行并收集截图

```bash
source venv/bin/activate
python3 run_all_tests.py  # 选择选项 3 - 运行所有测试
# 所有截图会保存在 screenshots/ 目录
```

### 3. 生成测试报告汇总

```bash
# 查看所有测试报告的通过率
for f in *_report_*.json; do
    echo "$f:"
    jq '.summary // {total, success, failed}' "$f"
    echo ""
done
```

### 4. 对比前后测试结果

```bash
# 保存基准测试
cp time_filter_report_*.json baseline_time_filter.json

# 运行新测试后对比
diff <(jq .summary baseline_time_filter.json) <(jq .summary time_filter_report_*.json | tail -1)
```

---

## 🔗 相关资源

- **项目文档**: https://github.com/NVIDIA-AI-Blueprints/streaming-data-to-rag
- **前端 UI**: http://localhost:3000
- **Playwright 文档**: https://playwright.dev/python/
- **Xvfb 文档**: `man xvfb-run`

---

## 📝 注意事项

1. **Xvfb 虚拟显示**: 虽然不会在屏幕上显示，但浏览器认为是真实环境
2. **截图质量**: 所有截图都是全页面高清截图
3. **测试数据**: 系统需要有已摄入的数据才能返回有意义的结果
4. **响应时间**: 包含了网络请求、AI 处理和渲染时间
5. **并发**: 不建议同时运行多个测试（会竞争虚拟显示）

---

## 🎬 示例输出

```
RAG 时间过滤功能 UI 自动化测试
使用 Playwright + Xvfb 虚拟显示
============================================================

访问前端: http://localhost:3000
测试开始时间: 2025-10-08T12:00:00+00:00
============================================================

============================================================
测试 1: 相对时间查询（Recent Summary）
============================================================

最近10分钟 - Channel 0
查询: Summarize the last 10 minutes on channel 0
    📸 截图: screenshots/query_20251008_120001.png
状态: ✓ 成功 | 响应时间: 2156ms

...

============================================================
测试报告
============================================================

总测试数: 19
成功: 17 (89.5%)
失败: 2 (10.5%)
平均响应时间: 2341ms

报告已保存: time_filter_report_20251008_120030.json

💡 提示: 所有截图已保存在 screenshots/ 目录
```

---

**版本**: 2.0 (Xvfb + 截图增强版)  
**最后更新**: 2025-10-08
