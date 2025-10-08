# RAG 系统时间过滤功能测试用例

## 测试环境配置

基于 NVIDIA Streaming Data to RAG 项目的时间过滤功能测试

---

## 1. Setup Test Environment

### 1.1 部署系统并配置测试音频文件

```bash
# 设置环境变量
export NVIDIA_API_KEY=<your-api-key>
export MODEL_DIRECTORY=~/.cache/nim
export REPLAY_FILES="sample_files/ai_gtc_1.mp3, sample_files/ai_gtc_2.mp3, sample_files/ai_gtc_3.mp3"
export REPLAY_TIME=3600
export REPLAY_MAX_FILE_SIZE=50

# 构建镜像
docker build -t ctx_rag -f external/context-aware-rag/docker/Dockerfile external/context-aware-rag
docker compose -f deploy/docker-compose.yaml --profile replay build

# 部署服务
docker compose -f external/context-aware-rag/docker/deploy/compose.yaml up -d
docker compose -f deploy/docker-compose.yaml --profile replay up -d
```

### 1.2 等待数据索引

```bash
# 检查服务健康状态
curl http://localhost:8000/health  # Retrieval service
curl http://localhost:8001/health  # Ingestion service
curl http://localhost:9091/healthz # Milvus
curl http://localhost:7474         # Neo4j

# 等待至少 5-10 分钟让数据被索引
# 访问 http://localhost:3000 查看 History 确认文档已 ingested
```

### 1.3 记录测试基准时间

```python
from datetime import datetime
import pytz

# 记录测试开始时间（UTC）
test_start_time = datetime.now(pytz.UTC)
print(f"Test Start Time (UTC): {test_start_time.isoformat()}")
print(f"Test Start Time (Local): {test_start_time.astimezone()}")
```

---

## 2. Execute Time Range Queries

### 2.1 相对时间查询（Recent Summary）

#### Test Case 2.1.1: 最近 N 分钟
```json
{
  "test_id": "TC_2.1.1",
  "description": "查询最近10分钟的内容",
  "queries": [
    {
      "query": "Summarize the last 10 minutes on channel 0",
      "expected_time_range": "past 600 seconds",
      "expected_streams": [0]
    },
    {
      "query": "What was discussed in the last 5 minutes on channel 1?",
      "expected_time_range": "past 300 seconds",
      "expected_streams": [1]
    },
    {
      "query": "Summarize the last 30 minutes across all channels",
      "expected_time_range": "past 1800 seconds",
      "expected_streams": [0, 1, 2, 3]
    }
  ]
}
```

#### Test Case 2.1.2: 最近 N 小时
```json
{
  "test_id": "TC_2.1.2",
  "description": "查询最近N小时的内容",
  "queries": [
    {
      "query": "Summarize the main topics discussed for the past hour",
      "expected_time_range": "past 3600 seconds",
      "expected_streams": "all"
    },
    {
      "query": "What topics were covered in the last 2 hours on channel 2?",
      "expected_time_range": "past 7200 seconds",
      "expected_streams": [2]
    }
  ]
}
```

#### Test Case 2.1.3: 排除特定通道
```json
{
  "test_id": "TC_2.1.3",
  "description": "查询时排除特定通道",
  "queries": [
    {
      "query": "Summarize the main topics discussed, excluding channel 2, for the past hour",
      "expected_time_range": "past 3600 seconds",
      "excluded_streams": [2],
      "expected_streams": [0, 1, 3]
    },
    {
      "query": "What was discussed in the last 15 minutes, excluding channels 0 and 3?",
      "expected_time_range": "past 900 seconds",
      "excluded_streams": [0, 3],
      "expected_streams": [1, 2]
    }
  ]
}
```

### 2.2 时间窗口查询（Time Window）

#### Test Case 2.2.1: N 分钟前
```json
{
  "test_id": "TC_2.2.1",
  "description": "查询特定时间点前的内容",
  "queries": [
    {
      "query": "What was the topic of conversation on channel 2 15 minutes ago?",
      "expected_center_time": "900 seconds ago",
      "expected_window": "5 minutes (default)",
      "expected_streams": [2]
    },
    {
      "query": "What was discussed on channel 0 5 minutes ago?",
      "expected_center_time": "300 seconds ago",
      "expected_window": "5 minutes (default)",
      "expected_streams": [0]
    }
  ]
}
```

#### Test Case 2.2.2: 时间范围查询
```json
{
  "test_id": "TC_2.2.2",
  "description": "查询特定时间范围内的内容",
  "queries": [
    {
      "query": "Between 2 minutes and half an hour ago, what was the most interesting fact you heard?",
      "expected_time_range": "120 to 1800 seconds ago",
      "expected_streams": "all"
    },
    {
      "query": "Between 5 and 20 minutes ago on channel 1, what topics were discussed?",
      "expected_time_range": "300 to 1200 seconds ago",
      "expected_streams": [1]
    },
    {
      "query": "What happened between 10 minutes and 1 hour ago on channel 3?",
      "expected_time_range": "600 to 3600 seconds ago",
      "expected_streams": [3]
    }
  ]
}
```

### 2.3 绝对时间查询（Specific Time）

#### Test Case 2.3.1: 小时制查询
```json
{
  "test_id": "TC_2.3.1",
  "description": "使用小时制查询特定时间",
  "queries": [
    {
      "query": "At 9 o'clock, what was the topic on channel 3?",
      "expected_time": "9:00 AM or 9:00 PM (most recent)",
      "expected_window": "5 minutes (default)",
      "expected_streams": [3]
    },
    {
      "query": "What was discussed at 2 PM on channel 0?",
      "expected_time": "14:00",
      "expected_window": "5 minutes (default)",
      "expected_streams": [0]
    }
  ]
}
```

#### Test Case 2.3.2: 指定时间窗口
```json
{
  "test_id": "TC_2.3.2",
  "description": "查询特定时间并指定时间窗口",
  "queries": [
    {
      "query": "At 10:00 PM, what was the topic on channel 3, using a 10 minute window?",
      "expected_time": "22:00",
      "expected_window": "10 minutes",
      "expected_streams": [3]
    },
    {
      "query": "At 3:30 PM, what was discussed on channel 2, using a 15 minute window?",
      "expected_time": "15:30",
      "expected_window": "15 minutes",
      "expected_streams": [2]
    }
  ]
}
```

#### Test Case 2.3.3: 完整时间戳格式
```json
{
  "test_id": "TC_2.3.3",
  "description": "使用完整时间戳格式查询",
  "queries": [
    {
      "query": "At 2025-10-08 14:30:00 UTC, what topics were covered on channel 1?",
      "expected_time": "2025-10-08T14:30:00Z",
      "expected_window": "5 minutes (default)",
      "expected_streams": [1]
    },
    {
      "query": "What was discussed at 11:45 AM on October 8th, 2025 on channel 0?",
      "expected_time": "2025-10-08T11:45:00Z",
      "expected_window": "5 minutes (default)",
      "expected_streams": [0]
    }
  ]
}
```

### 2.4 排除最近内容（Excluding Recent）

#### Test Case 2.4.1: 排除最近时间
```json
{
  "test_id": "TC_2.4.1",
  "description": "查询时排除最近的内容",
  "queries": [
    {
      "query": "What was the main topic of conversation on channel 0, excluding the past ten minutes?",
      "excluded_time_range": "past 600 seconds",
      "expected_streams": [0],
      "note": "Returns up to top_k documents prior to 600 seconds ago"
    },
    {
      "query": "Summarize the topics on channel 2, excluding the last 5 minutes",
      "excluded_time_range": "past 300 seconds",
      "expected_streams": [2]
    },
    {
      "query": "What was discussed on all channels, excluding the past hour?",
      "excluded_time_range": "past 3600 seconds",
      "expected_streams": "all"
    }
  ]
}
```

---

## 3. Validate Boundary Conditions

### Test Case 3.1: 时间窗口边界

```json
{
  "test_id": "TC_3.1",
  "description": "测试时间窗口边界",
  "test_cases": [
    {
      "name": "窗口起始边界",
      "query": "What was discussed between exactly 10 minutes and 9 minutes ago on channel 0?",
      "expected_behavior": "Returns documents with timestamps: now() - 600s <= timestamp <= now() - 540s"
    },
    {
      "name": "窗口结束边界",
      "query": "What topics were covered from 5 minutes ago to now on channel 1?",
      "expected_behavior": "Returns documents with timestamps: now() - 300s <= timestamp <= now()"
    },
    {
      "name": "单秒窗口",
      "query": "What was happening at exactly 12:00:00 PM, within 1 second?",
      "expected_behavior": "Returns documents within 1 second window around 12:00:00"
    },
    {
      "name": "零窗口（精确时间）",
      "query": "What was the exact content at timestamp 2025-10-08T12:00:00Z?",
      "expected_behavior": "Returns documents at exact timestamp or uses default 5-minute window"
    }
  ]
}
```

### Test Case 3.2: 空时间窗口

```json
{
  "test_id": "TC_3.2",
  "description": "测试空时间窗口（无数据）",
  "test_cases": [
    {
      "name": "未来时间窗口",
      "query": "What will be discussed 10 minutes from now on channel 0?",
      "expected_result": "No documents (future time)",
      "expected_message": "No data available for specified time range"
    },
    {
      "name": "数据开始前的时间",
      "query": "What was discussed 10 hours ago on channel 2?",
      "expected_result": "No documents (before data collection started)",
      "expected_message": "No data available for specified time range"
    },
    {
      "name": "通道无数据窗口",
      "query": "What was discussed on channel 5 in the last 10 minutes?",
      "expected_result": "No documents (invalid channel)",
      "expected_message": "No data available for channel 5"
    }
  ]
}
```

### Test Case 3.3: 跨时间范围查询

```json
{
  "test_id": "TC_3.3",
  "description": "测试跨越多个时间段的查询",
  "test_cases": [
    {
      "name": "跨小时查询",
      "query": "What was discussed between 11:45 AM and 12:15 PM on channel 0?",
      "expected_behavior": "Returns documents across hour boundary",
      "time_range": "30 minutes spanning 11:45-12:15"
    },
    {
      "name": "跨天查询（如适用）",
      "query": "What topics were covered between 11:30 PM yesterday and 12:30 AM today?",
      "expected_behavior": "Returns documents across day boundary",
      "time_range": "1 hour spanning midnight"
    },
    {
      "name": "多段时间组合",
      "query": "What were the main topics at 9 AM, 12 PM, and 3 PM on channel 1?",
      "expected_behavior": "Returns documents from three separate time windows",
      "note": "May require multiple queries or custom implementation"
    }
  ]
}
```

---

## 4. Performance Verification

### Test Case 4.1: 响应时间测量

```python
import time
import requests

def measure_query_performance(query, endpoint="http://localhost:8000/query"):
    """测量查询响应时间"""
    
    queries_to_test = [
        # 无时间过滤
        {"query": "What are the main topics discussed?", "has_time_filter": False},
        
        # 简单时间过滤
        {"query": "Summarize the last 10 minutes on channel 0", "has_time_filter": True},
        
        # 复杂时间过滤
        {"query": "Between 5 and 30 minutes ago, what was discussed on channel 2?", "has_time_filter": True},
        
        # 多条件过滤
        {"query": "Summarize the last hour, excluding channel 3, with a focus on technical topics", "has_time_filter": True},
    ]
    
    results = []
    for q in queries_to_test:
        start_time = time.time()
        
        response = requests.post(endpoint, json={"query": q["query"]})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        results.append({
            "query": q["query"],
            "has_time_filter": q["has_time_filter"],
            "response_time_ms": response_time * 1000,
            "status_code": response.status_code,
            "result_count": len(response.json().get("documents", []))
        })
    
    return results

# 运行性能测试
perf_results = measure_query_performance()

# 分析结果
for result in perf_results:
    print(f"Query: {result['query'][:50]}...")
    print(f"  Time Filter: {result['has_time_filter']}")
    print(f"  Response Time: {result['response_time_ms']:.2f}ms")
    print(f"  Documents: {result['result_count']}")
    print()

# 性能基准
acceptable_response_time_ms = 2000  # 2秒
assert all(r['response_time_ms'] < acceptable_response_time_ms for r in perf_results), \
    "Some queries exceeded acceptable response time"
```

### Test Case 4.2: 对比有无时间过滤的性能

```json
{
  "test_id": "TC_4.2",
  "description": "对比有无时间过滤的查询性能",
  "test_pairs": [
    {
      "without_filter": "What are the main topics about AI?",
      "with_filter": "What are the main topics about AI in the last 15 minutes?",
      "expected_difference": "< 500ms overhead for time filtering"
    },
    {
      "without_filter": "Summarize the discussion on channel 0",
      "with_filter": "Summarize the discussion on channel 0 between 10 and 20 minutes ago",
      "expected_difference": "< 500ms overhead for time filtering"
    }
  ],
  "acceptance_criteria": {
    "max_overhead_ms": 500,
    "max_response_time_ms": 2000
  }
}
```

### Test Case 4.3: 不同时间窗口大小的性能

```json
{
  "test_id": "TC_4.3",
  "description": "测试不同时间窗口大小的查询性能",
  "queries": [
    {"query": "Summarize the last 1 minute on channel 0", "window_seconds": 60},
    {"query": "Summarize the last 5 minutes on channel 0", "window_seconds": 300},
    {"query": "Summarize the last 15 minutes on channel 0", "window_seconds": 900},
    {"query": "Summarize the last 30 minutes on channel 0", "window_seconds": 1800},
    {"query": "Summarize the last hour on channel 0", "window_seconds": 3600}
  ],
  "expected_behavior": "Response time should scale linearly with window size",
  "max_acceptable_slope": "< 0.5ms per second of window"
}
```

---

## 5. Result Validation

### Test Case 5.1: 时间戳准确性验证

```python
from datetime import datetime, timedelta
import pytz

def validate_timestamp_accuracy(query, expected_time_range, results):
    """验证返回文档的时间戳是否在预期范围内"""
    
    test_cases = [
        {
            "query": "Summarize the last 10 minutes on channel 0",
            "expected_start": datetime.now(pytz.UTC) - timedelta(minutes=10),
            "expected_end": datetime.now(pytz.UTC),
            "stream": 0
        },
        {
            "query": "What was discussed 15 minutes ago on channel 2?",
            "expected_start": datetime.now(pytz.UTC) - timedelta(minutes=17.5),
            "expected_end": datetime.now(pytz.UTC) - timedelta(minutes=12.5),
            "stream": 2,
            "window": "5 minutes (default)"
        },
        {
            "query": "Between 5 and 30 minutes ago, what was discussed?",
            "expected_start": datetime.now(pytz.UTC) - timedelta(minutes=30),
            "expected_end": datetime.now(pytz.UTC) - timedelta(minutes=5),
            "stream": "all"
        }
    ]
    
    for test in test_cases:
        # 执行查询并获取结果
        response = execute_query(test["query"])
        documents = response.get("documents", [])
        
        # 验证每个文档的时间戳
        for doc in documents:
            doc_timestamp = datetime.fromisoformat(doc["timestamp"])
            
            assert test["expected_start"] <= doc_timestamp <= test["expected_end"], \
                f"Document timestamp {doc_timestamp} not in range [{test['expected_start']}, {test['expected_end']}]"
            
            if test["stream"] != "all":
                assert doc["stream"] == test["stream"], \
                    f"Document stream {doc['stream']} does not match expected {test['stream']}"
        
        print(f"✓ Query '{test['query']}': {len(documents)} documents, all timestamps valid")

# 运行验证
validate_timestamp_accuracy()
```

### Test Case 5.2: 文档完整性验证

```json
{
  "test_id": "TC_5.2",
  "description": "验证返回文档的完整性",
  "validation_checks": [
    {
      "name": "文档数量检查",
      "query": "Summarize the last 10 minutes on channel 0",
      "validation": "Count of returned documents <= top_k (default 25)",
      "check_function": "len(documents) <= 25"
    },
    {
      "name": "文档内容完整性",
      "query": "What was discussed 5 minutes ago?",
      "validation": "Each document has required fields",
      "required_fields": ["timestamp", "stream", "content", "metadata"]
    },
    {
      "name": "无重复文档",
      "query": "Summarize the last 15 minutes",
      "validation": "No duplicate documents in results",
      "check_function": "len(documents) == len(set(doc['id'] for doc in documents))"
    },
    {
      "name": "文档排序",
      "query": "What happened in the last 20 minutes on channel 1?",
      "validation": "Documents sorted by timestamp (descending)",
      "check_function": "documents == sorted(documents, key=lambda x: x['timestamp'], reverse=True)"
    }
  ]
}
```

### Test Case 5.3: 查询一致性验证

```json
{
  "test_id": "TC_5.3",
  "description": "验证相同查询返回一致的结果",
  "test_cases": [
    {
      "name": "相同查询重复执行",
      "query": "Summarize the last 5 minutes on channel 0",
      "repetitions": 3,
      "expected": "All executions return same document IDs (if within same time window)",
      "tolerance": "Allow for new documents added during testing"
    },
    {
      "name": "等价查询一致性",
      "queries": [
        "What was discussed in the last 10 minutes?",
        "Summarize the past 10 minutes",
        "What happened in the last 600 seconds?"
      ],
      "expected": "All queries return same or similar results",
      "tolerance": "Minor variations acceptable due to LLM interpretation"
    },
    {
      "name": "时间窗口一致性",
      "queries": [
        "What was discussed at 2 PM with a 10 minute window?",
        "What happened between 1:55 PM and 2:05 PM?"
      ],
      "expected": "Both queries return same documents",
      "tolerance": "Exact match expected"
    }
  ]
}
```

---

## 6. Error Handling

### Test Case 6.1: 无效时间格式

```json
{
  "test_id": "TC_6.1",
  "description": "测试无效时间格式的处理",
  "test_cases": [
    {
      "query": "What was discussed at 25:00 on channel 0?",
      "error_type": "Invalid hour format",
      "expected_behavior": "Graceful error or interpret as 1:00 AM",
      "expected_message": "Invalid time format or reasonable interpretation"
    },
    {
      "query": "Summarize the last -10 minutes",
      "error_type": "Negative time range",
      "expected_behavior": "Error or interpret as future (no results)",
      "expected_message": "Invalid time range"
    },
    {
      "query": "What happened on February 30th?",
      "error_type": "Invalid date",
      "expected_behavior": "Error message",
      "expected_message": "Invalid date"
    },
    {
      "query": "Summarize the last eleventy minutes",
      "error_type": "Non-numeric time value",
      "expected_behavior": "Error or request clarification",
      "expected_message": "Could not parse time value"
    },
    {
      "query": "What was discussed at 2025-13-45T99:99:99Z?",
      "error_type": "Malformed ISO timestamp",
      "expected_behavior": "Error message",
      "expected_message": "Invalid timestamp format"
    }
  ]
}
```

### Test Case 6.2: 时间范围错误

```json
{
  "test_id": "TC_6.2",
  "description": "测试时间范围错误的处理",
  "test_cases": [
    {
      "query": "What was discussed between 30 minutes ago and 1 hour ago?",
      "error_type": "Inverted time range (end before start)",
      "expected_behavior": "Swap times or error message",
      "expected_message": "Invalid time range: end time is before start time"
    },
    {
      "query": "Summarize from 2025-10-08T10:00:00Z to 2025-10-08T09:00:00Z",
      "error_type": "End time before start time",
      "expected_behavior": "Error message or auto-correct",
      "expected_message": "End time must be after start time"
    },
    {
      "query": "What happened in a 0 second window at 2 PM?",
      "error_type": "Zero-length time window",
      "expected_behavior": "Use default window or single-point query",
      "expected_message": "Using default 5-minute window"
    },
    {
      "query": "Summarize the last 100 hours",
      "error_type": "Excessively large time window",
      "expected_behavior": "Warning or limit to available data",
      "expected_message": "Time range exceeds available data or system limits"
    }
  ]
}
```

### Test Case 6.3: 错误消息验证

```python
def test_error_messages():
    """验证错误消息的质量和有用性"""
    
    test_cases = [
        {
            "query": "What was discussed at 99:99?",
            "check": "Error message is user-friendly",
            "criteria": [
                "Message is in plain language",
                "Message suggests correct format",
                "Message doesn't expose system internals"
            ]
        },
        {
            "query": "Summarize channel 999 from the last hour",
            "check": "Error identifies specific problem (invalid channel)",
            "criteria": [
                "Mentions channel number is invalid",
                "Lists valid channel numbers",
                "Doesn't crash or return generic error"
            ]
        },
        {
            "query": "What happened at timestamp abc123?",
            "check": "Error provides example of correct format",
            "criteria": [
                "Shows example timestamp format",
                "Suggests using relative time as alternative",
                "Clear and actionable"
            ]
        }
    ]
    
    for test in test_cases:
        response = execute_query(test["query"])
        
        if response.get("error"):
            error_msg = response["error"]
            print(f"\nQuery: {test['query']}")
            print(f"Error: {error_msg}")
            print(f"Criteria: {test['criteria']}")
            
            # 验证错误消息质量
            assert len(error_msg) > 10, "Error message too short"
            assert not any(x in error_msg.lower() for x in ["exception", "traceback", "null pointer"]), \
                "Error message exposes system internals"

# 运行测试
test_error_messages()
```

---

## 7. 综合测试场景

### Test Case 7.1: 端到端用户场景

```json
{
  "test_id": "TC_7.1",
  "description": "模拟真实用户使用场景",
  "scenarios": [
    {
      "name": "情报分析师场景",
      "workflow": [
        {
          "step": 1,
          "action": "获取最近活动概览",
          "query": "Summarize all channels from the last 30 minutes"
        },
        {
          "step": 2,
          "action": "深入特定通道",
          "query": "What specific topics were discussed on channel 2 in the last 15 minutes?"
        },
        {
          "step": 3,
          "action": "对比历史数据",
          "query": "How does the last 15 minutes on channel 2 compare to 30 minutes ago?"
        },
        {
          "step": 4,
          "action": "排除噪音数据",
          "query": "What were the key topics on all channels in the past hour, excluding the last 5 minutes?"
        }
      ]
    },
    {
      "name": "无线电爱好者场景",
      "workflow": [
        {
          "step": 1,
          "action": "检查特定时间段",
          "query": "What was broadcasted at 9 AM on channel 0?"
        },
        {
          "step": 2,
          "action": "查找有趣内容",
          "query": "Between 8 AM and 10 AM, what was the most interesting fact mentioned?"
        },
        {
          "step": 3,
          "action": "跟踪特定主题",
          "query": "When was machine learning discussed in the last 2 hours?"
        }
      ]
    }
  ]
}
```

### Test Case 7.2: 压力测试

```python
import concurrent.futures
import time

def stress_test_time_queries(num_concurrent=10, num_iterations=100):
    """压力测试时间查询功能"""
    
    queries = [
        "Summarize the last 5 minutes on channel 0",
        "What was discussed 10 minutes ago on channel 1?",
        "Between 5 and 15 minutes ago, what topics were covered?",
        "Summarize the last hour, excluding channel 2",
        "What was the main topic at 2 PM on channel 3?"
    ]
    
    def execute_query_batch(batch_id):
        results = []
        for i in range(num_iterations // num_concurrent):
            query = queries[i % len(queries)]
            start = time.time()
            
            try:
                response = requests.post("http://localhost:8000/query", 
                                       json={"query": query})
                elapsed = time.time() - start
                
                results.append({
                    "batch_id": batch_id,
                    "iteration": i,
                    "query": query,
                    "success": response.status_code == 200,
                    "response_time_ms": elapsed * 1000
                })
            except Exception as e:
                results.append({
                    "batch_id": batch_id,
                    "iteration": i,
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    # 并发执行查询
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(execute_query_batch, i) 
                  for i in range(num_concurrent)]
        all_results = []
        for future in concurrent.futures.as_completed(futures):
            all_results.extend(future.result())
    
    # 分析结果
    success_rate = sum(1 for r in all_results if r["success"]) / len(all_results)
    avg_response_time = sum(r.get("response_time_ms", 0) for r in all_results if r["success"]) / \
                       sum(1 for r in all_results if r["success"])
    
    print(f"\n=== Stress Test Results ===")
    print(f"Total Queries: {len(all_results)}")
    print(f"Success Rate: {success_rate * 100:.2f}%")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"Failed Queries: {len(all_results) - sum(1 for r in all_results if r['success'])}")
    
    assert success_rate > 0.95, f"Success rate {success_rate} below threshold"
    assert avg_response_time < 3000, f"Average response time {avg_response_time}ms exceeds threshold"

# 运行压力测试
stress_test_time_queries(num_concurrent=10, num_iterations=100)
```

---

## 8. 测试执行清单

### 执行前检查
- [ ] 所有服务运行正常且健康
- [ ] 至少 10 分钟的数据已被索引
- [ ] 记录当前 UTC 时间作为测试基准
- [ ] 确认 `top_k` 和 `batch_size` 配置值
- [ ] 查看 History 页面确认文档状态

### 测试执行顺序
1. [ ] Setup Test Environment (Section 1)
2. [ ] Execute Time Range Queries (Section 2)
3. [ ] Validate Boundary Conditions (Section 3)
4. [ ] Performance Verification (Section 4)
5. [ ] Result Validation (Section 5)
6. [ ] Error Handling (Section 6)
7. [ ] Comprehensive Scenarios (Section 7)

### 结果记录
- [ ] 记录每个测试用例的通过/失败状态
- [ ] 记录响应时间数据
- [ ] 截取关键测试结果的截图
- [ ] 记录任何异常或意外行为
- [ ] 生成测试报告

---

## 参考配置

### 系统配置
- **配置文件**: `external/context-aware-rag/config/config.yaml`
- **Top K**: 默认 25（可配置）
- **Batch Size**: 可配置
- **默认时间窗口**: 5 分钟
- **时区**: UTC

### API 端点
- Frontend: <http://localhost:3000>
- Retrieval: <http://localhost:8000>
- Ingestion: <http://localhost:8001>
- Milvus: <http://localhost:9091>
- Neo4j: <http://localhost:7474>

---

## 注意事项

1. **所有时间均为 UTC** - 查看 transcript history 页面获取相对时间
2. **文档批处理** - 文档不会立即被索引，需等待批次完成
3. **默认窗口** - 未指定窗口时，使用 5 分钟默认窗口
4. **Channel/Stream** - 系统使用 stream ID (0, 1, 2, 3)
5. **性能基准** - 响应时间应 < 2 秒
