# 时间过滤功能测试用例 (REQ-01)

## 测试组 1: 相对时间查询 (Recent Summary)

### TC-1.1: 最近10分钟 - 单通道
**输入查询：** `Summarize the last 10 minutes on channel 0`
**期待结果：** 
- 返回 channel 0 最近10分钟的音频转录摘要
- 响应时间 < 5秒
- 时间戳在当前时间往前10分钟范围内

### TC-1.2: 最近5分钟 - 不同通道
**输入查询：** `What was discussed in the last 5 minutes on channel 1?`
**期待结果：**
- 返回 channel 1 最近5分钟的讨论内容
- 响应时间 < 5秒
- 正确识别"last 5 minutes"时间范围

### TC-1.3: 最近30分钟 - 所有通道
**输入查询：** `Summarize the last 30 minutes across all channels`
**期待结果：**
- 返回所有通道（ch0, ch1, ch2）最近30分钟的摘要
- 响应时间 < 10秒
- 内容应包含多个通道的信息

### TC-1.4: 最近1小时
**输入查询：** `Summarize the main topics discussed for the past hour`
**期待结果：**
- 返回过去1小时的主要话题摘要
- 响应时间 < 10秒
- 正确识别"past hour"为60分钟

### TC-1.5: 排除特定通道
**输入查询：** `Summarize the main topics discussed, excluding channel 2, for the past hour`
**期待结果：**
- 返回过去1小时的摘要，但不包括 channel 2 的内容
- 响应时间 < 10秒
- 正确过滤掉 channel 2

---

## 测试组 2: 特定时间窗口查询

### TC-2.1: N分钟前的内容
**输入查询：** `What was the topic of conversation on channel 2 15 minutes ago?`
**期待结果：**
- 返回 channel 2 大约15分钟前的对话主题
- 响应时间 < 5秒
- 时间戳在当前时间往前15分钟左右

### TC-2.2: 时间范围查询（分钟）
**输入查询：** `Between 2 minutes and half an hour ago, what was the most interesting fact you heard?`
**期待结果：**
- 返回2-30分钟前最有趣的事实
- 响应时间 < 8秒
- 正确解析"half an hour"为30分钟
- 时间戳在指定范围内

### TC-2.3: 时间范围查询（指定通道）
**输入查询：** `Between 5 and 20 minutes ago on channel 1, what topics were discussed?`
**期待结果：**
- 返回 channel 1 在5-20分钟前讨论的话题
- 响应时间 < 5秒
- 时间戳准确在5-20分钟前的范围内

---

## 测试组 3: 排除最近内容

### TC-3.1: 排除最近10分钟
**输入查询：** `What was the main topic of conversation on channel 0, excluding the past ten minutes?`
**期待结果：**
- 返回 channel 0 的历史对话主题，但不包括最近10分钟
- 响应时间 < 8秒
- 所有返回的时间戳应该早于10分钟前

### TC-3.2: 排除最近5分钟
**输入查询：** `Summarize the topics on channel 2, excluding the last 5 minutes`
**期待结果：**
- 返回 channel 2 的话题摘要，但不包括最近5分钟
- 响应时间 < 8秒
- 时间戳应该早于5分钟前

---

## 测试组 4: 边界条件测试

### TC-4.1: 精确时间窗口
**输入查询：** `What was discussed between exactly 10 minutes and 9 minutes ago on channel 0?`
**期待结果：**
- 返回 channel 0 在9-10分钟前这1分钟窗口内的内容
- 响应时间 < 5秒
- 如果该时间段无数据，应明确说明
- 时间戳精确在9-10分钟前

### TC-4.2: 未来时间（应无结果）
**输入查询：** `What will be discussed 10 minutes from now on channel 0?`
**期待结果：**
- 系统应识别这是未来时间
- 返回提示：无法查询未来数据
- 响应时间 < 3秒
- 或者返回空结果并说明原因

### TC-4.3: 很久以前（应无/少结果）
**输入查询：** `What was discussed 10 hours ago on channel 2?`
**期待结果：**
- 如果10小时前没有数据，应明确说明
- 返回消息如："No data found for that time range"
- 响应时间 < 5秒
- 不应返回错误，而是友好提示

---

## 测试组 5: 错误处理

### TC-5.1: 无效时间格式
**输入查询：** `What was discussed at 25:00 on channel 0?`
**期待结果：**
- 识别 25:00 是无效时间格式
- 返回友好错误提示
- 建议正确的时间格式
- 响应时间 < 3秒

### TC-5.2: 负时间范围
**输入查询：** `Summarize the last -10 minutes`
**期待结果：**
- 识别负数时间无效
- 返回错误提示或自动纠正为正数
- 响应时间 < 3秒

### TC-5.3: 无效通道号
**输入查询：** `Summarize channel 999 from the last hour`
**期待结果：**
- 识别 channel 999 不存在
- 返回可用通道列表（如：channel 0, 1, 2）
- 响应时间 < 3秒

### TC-5.4: 倒序时间范围
**输入查询：** `What was discussed between 30 minutes ago and 1 hour ago?`
**期待结果：**
- 系统应自动纠正时间顺序（应该是1小时前到30分钟前）
- 或者返回提示：时间范围顺序错误
- 仍然返回正确时间范围的结果

---

## 性能基准

| 测试类型 | 期待响应时间 | 备注 |
|---------|-------------|------|
| 单通道简单查询 | < 5秒 | 如 TC-1.1, TC-1.2 |
| 多通道查询 | < 10秒 | 如 TC-1.3, TC-1.4 |
| 复杂范围查询 | < 8秒 | 如 TC-2.2, TC-3.1 |
| 错误处理 | < 3秒 | 如 TC-5.x 系列 |

---

## 数据验证要点

对于每个成功的查询，验证：

1. **时间戳准确性**
   - 返回的数据时间戳在查询范围内
   - 边界时间点处理正确

2. **内容完整性**
   - 指定时间范围内的所有相关数据都被返回
   - 没有遗漏或重复

3. **通道过滤正确性**
   - 查询指定通道时，只返回该通道数据
   - 排除通道时，正确过滤

4. **响应质量**
   - 摘要准确反映原始转录内容
   - 时间表述清晰
   - 无数据时有明确说明

---

## 快速测试命令

```bash
# 运行时间过滤完整测试套件
cd /localhome/keystone/jupyter_workspace/sdr-testing/qa-tests
source venv/bin/activate
xvfb-run -a --server-args="-screen 0 1920x1080x24" python3 test_rag_time_filtering.py

# 查看测试报告
ls -lt *_report_*.json | head -1

# 查看截图
ls -lt screenshots/ | head -10
```

