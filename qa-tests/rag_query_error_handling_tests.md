# RAG 系统查询错误处理与智能提示测试用例

## REQ-02: 查询错误处理增强

**目标**: 通过智能提示和自动纠正增强查询错误处理，将模糊或不完整的查询转换为可执行请求，提升用户体验。

基于 NVIDIA Streaming Data to RAG 项目: https://github.com/NVIDIA-AI-Blueprints/streaming-data-to-rag

---

## 测试概述

### 核心功能
- **智能提示**: 识别缺失信息并提供补充建议
- **自动纠正**: 修正格式错误和词序问题
- **清晰错误消息**: 提供可操作的具体修复建议
- **用户引导**: 对完全模糊的查询提供帮助

### 测试范围
1. 查询解析测试
2. 智能提示验证
3. 自动纠正测试
4. 错误消息验证
5. 边缘案例测试

---

## 1. Test Query Parsing（查询解析测试）

### Test Case 1.1: 缺少通道号的查询

#### TC_1.1.1: 完全缺少通道号
```json
{
  "test_id": "TC_1.1.1",
  "category": "Missing Channel Number",
  "test_cases": [
    {
      "input_query": "Summarize the last 10 minutes",
      "missing_info": "channel number",
      "expected_behavior": "prompt_or_default",
      "smart_prompt": {
        "message": "Which channel would you like to summarize? Available channels: 0, 1, 2, 3",
        "suggestions": [
          "Summarize the last 10 minutes on channel 0",
          "Summarize the last 10 minutes on all channels"
        ],
        "default_action": "Query all channels by default"
      },
      "auto_correction": "Summarize the last 10 minutes on all channels"
    },
    {
      "input_query": "What topics were discussed in the past hour?",
      "missing_info": "channel number",
      "smart_prompt": {
        "message": "I can search across all channels or a specific channel. Which would you prefer?",
        "suggestions": [
          "What topics were discussed in the past hour on channel 0?",
          "What topics were discussed in the past hour on channel 1?",
          "What topics were discussed in the past hour on all channels?"
        ]
      }
    },
    {
      "input_query": "Show me recent transcripts",
      "missing_info": ["channel number", "time range"],
      "smart_prompt": {
        "message": "To show recent transcripts, I need:\n- Which channel? (0, 1, 2, 3, or all)\n- How recent? (e.g., last 10 minutes, past hour)",
        "suggestions": [
          "Show me transcripts from the last 10 minutes on channel 0",
          "Show me transcripts from the past hour on all channels"
        ]
      }
    }
  ]
}
```

#### TC_1.1.2: 通道号格式错误
```json
{
  "test_id": "TC_1.1.2",
  "category": "Incorrect Channel Format",
  "test_cases": [
    {
      "input_query": "Summarize channel zero from the last 10 minutes",
      "error_type": "text_instead_of_number",
      "auto_correction": {
        "corrected_query": "Summarize channel 0 from the last 10 minutes",
        "correction_note": "Converted 'zero' to '0'"
      }
    },
    {
      "input_query": "What was discussed on stream 2 in the past hour?",
      "error_type": "wrong_terminology",
      "auto_correction": {
        "corrected_query": "What was discussed on channel 2 in the past hour?",
        "correction_note": "Recognized 'stream' as synonym for 'channel'"
      }
    },
    {
      "input_query": "Summarize frequency 1 from the last 15 minutes",
      "error_type": "alternative_terminology",
      "auto_correction": {
        "corrected_query": "Summarize channel 1 from the last 15 minutes",
        "correction_note": "Recognized 'frequency' as referring to channel"
      }
    },
    {
      "input_query": "What happened on ch 3 recently?",
      "error_type": "abbreviation",
      "auto_correction": {
        "corrected_query": "What happened on channel 3 recently?",
        "correction_note": "Expanded 'ch' to 'channel'"
      },
      "additional_prompt": "How recent? (e.g., last 5 minutes, past hour)"
    }
  ]
}
```

#### TC_1.1.3: 无效通道号
```json
{
  "test_id": "TC_1.1.3",
  "category": "Invalid Channel Number",
  "test_cases": [
    {
      "input_query": "Summarize channel 5 from the last 10 minutes",
      "error_type": "out_of_range",
      "error_message": {
        "message": "Channel 5 is not available.",
        "details": "Available channels: 0, 1, 2, 3",
        "suggestion": "Did you mean channel 3? Or would you like to query all channels?"
      },
      "suggested_corrections": [
        "Summarize channel 3 from the last 10 minutes",
        "Summarize all channels from the last 10 minutes"
      ]
    },
    {
      "input_query": "What was on channel -1 fifteen minutes ago?",
      "error_type": "negative_channel",
      "error_message": {
        "message": "Channel -1 is not valid.",
        "details": "Channel numbers must be between 0 and 3",
        "suggestion": "Please specify a channel between 0 and 3"
      }
    },
    {
      "input_query": "Summarize channel 2.5 from the past hour",
      "error_type": "non_integer",
      "auto_correction": {
        "corrected_query": "Summarize channel 2 from the past hour",
        "correction_note": "Rounded 2.5 to nearest integer (2)"
      }
    }
  ]
}
```

### Test Case 1.2: 缺少时间信息的查询

#### TC_1.2.1: 完全缺少时间信息
```json
{
  "test_id": "TC_1.2.1",
  "category": "Missing Time Information",
  "test_cases": [
    {
      "input_query": "What was discussed on channel 0?",
      "missing_info": "time range",
      "smart_prompt": {
        "message": "When would you like to search? Options:",
        "options": [
          "Recent (last 10 minutes)",
          "Past hour",
          "Today",
          "Specific time range"
        ],
        "suggestions": [
          "What was discussed on channel 0 in the last 10 minutes?",
          "What was discussed on channel 0 in the past hour?",
          "What was discussed on channel 0 today?"
        ]
      },
      "default_behavior": "Use default time window (last 10 minutes)"
    },
    {
      "input_query": "Summarize channel 2",
      "missing_info": "time range",
      "auto_correction": {
        "corrected_query": "Summarize channel 2 from the last 10 minutes",
        "correction_note": "Applied default time window"
      }
    },
    {
      "input_query": "Tell me about the AI discussion",
      "missing_info": ["channel", "time range"],
      "smart_prompt": {
        "message": "To find discussions about AI, I need:\n- Which channel to search? (or all channels)\n- What time period? (e.g., past hour, today)",
        "suggestions": [
          "Tell me about the AI discussion in the past hour on all channels",
          "Tell me about the AI discussion today on channel 0"
        ]
      }
    }
  ]
}
```

#### TC_1.2.2: 模糊的时间描述
```json
{
  "test_id": "TC_1.2.2",
  "category": "Vague Time Descriptions",
  "test_cases": [
    {
      "input_query": "What was discussed on channel 1 recently?",
      "vague_term": "recently",
      "auto_correction": {
        "corrected_query": "What was discussed on channel 1 in the last 10 minutes?",
        "correction_note": "Interpreted 'recently' as last 10 minutes"
      },
      "clarification_prompt": {
        "message": "By 'recently', do you mean:",
        "options": [
          "Last 5 minutes",
          "Last 10 minutes (default)",
          "Last 30 minutes",
          "Past hour"
        ]
      }
    },
    {
      "input_query": "Summarize channel 0 a while ago",
      "vague_term": "a while ago",
      "smart_prompt": {
        "message": "'A while ago' is ambiguous. Please specify:",
        "suggestions": [
          "15 minutes ago",
          "30 minutes ago",
          "1 hour ago"
        ]
      }
    },
    {
      "input_query": "What happened earlier on channel 3?",
      "vague_term": "earlier",
      "auto_correction": {
        "corrected_query": "What happened on channel 3 30 minutes ago?",
        "correction_note": "Interpreted 'earlier' as 30 minutes ago with 5-minute window"
      }
    },
    {
      "input_query": "Show me old transcripts from channel 2",
      "vague_term": "old",
      "smart_prompt": {
        "message": "How far back would you like to search?",
        "options": [
          "1 hour ago",
          "2 hours ago",
          "Start of recording session"
        ],
        "note": "Data is only available from the recording start time"
      }
    }
  ]
}
```

#### TC_1.2.3: 时间格式错误
```json
{
  "test_id": "TC_1.2.3",
  "category": "Time Format Errors",
  "test_cases": [
    {
      "input_query": "What was on channel 0 at 25:00?",
      "error_type": "invalid_hour",
      "error_message": {
        "message": "Invalid time format: 25:00 is not a valid hour",
        "details": "Hours must be between 0-23 (24-hour format) or 1-12 with AM/PM",
        "suggestion": "Did you mean 1:00 AM (01:00)?"
      },
      "auto_correction": {
        "corrected_query": "What was on channel 0 at 01:00?",
        "correction_note": "Corrected 25:00 to 01:00"
      }
    },
    {
      "input_query": "Summarize channel 1 from last 90 seconds",
      "error_type": "unusual_unit",
      "auto_correction": {
        "corrected_query": "Summarize channel 1 from the last 1.5 minutes",
        "correction_note": "Converted 90 seconds to 1.5 minutes"
      }
    },
    {
      "input_query": "What happened ten mins ago on channel 2?",
      "error_type": "informal_abbreviation",
      "auto_correction": {
        "corrected_query": "What happened 10 minutes ago on channel 2?",
        "correction_note": "Standardized 'ten mins' to '10 minutes'"
      }
    },
    {
      "input_query": "Show me channel 0 from 2pm to 3pm yesterday",
      "error_type": "relative_date",
      "smart_prompt": {
        "message": "Data is only available from the current recording session",
        "available_range": "From [session_start_time] to now",
        "suggestion": "Would you like to search a recent time range instead?"
      }
    }
  ]
}
```

### Test Case 1.3: 格式错误的查询

#### TC_1.3.1: 语法错误
```json
{
  "test_id": "TC_1.3.1",
  "category": "Syntax Errors",
  "test_cases": [
    {
      "input_query": "channel 0 what last 10 minutes",
      "error_type": "broken_syntax",
      "auto_correction": {
        "corrected_query": "What was on channel 0 in the last 10 minutes?",
        "correction_note": "Reconstructed proper sentence structure"
      }
    },
    {
      "input_query": "summarize from 10 minutes channel 2",
      "error_type": "wrong_word_order",
      "auto_correction": {
        "corrected_query": "Summarize channel 2 from the last 10 minutes",
        "correction_note": "Reordered words to proper syntax"
      }
    },
    {
      "input_query": "15 mins ago 1 what?",
      "error_type": "incomplete_sentence",
      "smart_prompt": {
        "message": "I couldn't understand your query. Did you mean:",
        "suggestions": [
          "What was on channel 1 15 minutes ago?",
          "Summarize channel 1 from 15 minutes ago"
        ]
      }
    }
  ]
}
```

#### TC_1.3.2: 拼写错误
```json
{
  "test_id": "TC_1.3.2",
  "category": "Spelling Errors",
  "test_cases": [
    {
      "input_query": "Summerize channal 0 from the last our",
      "error_type": "multiple_typos",
      "auto_correction": {
        "corrected_query": "Summarize channel 0 from the last hour",
        "corrections": [
          "Summerize → Summarize",
          "channal → channel",
          "our → hour"
        ]
      }
    },
    {
      "input_query": "What was discused on chanel 2 recntly?",
      "error_type": "typos",
      "auto_correction": {
        "corrected_query": "What was discussed on channel 2 recently?",
        "corrections": [
          "discused → discussed",
          "chanel → channel",
          "recntly → recently"
        ]
      }
    }
  ]
}
```

---

## 2. Verify Smart Prompting（智能提示验证）

### Test Case 2.1: 识别缺失信息

#### TC_2.1.1: 单一缺失信息识别
```json
{
  "test_id": "TC_2.1.1",
  "category": "Single Missing Info Detection",
  "test_cases": [
    {
      "input_query": "Summarize the last 10 minutes",
      "detected_missing": ["channel"],
      "detected_present": ["time_range"],
      "validation": {
        "correctly_identified": true,
        "prompt_quality": "Should ask for channel number",
        "provides_options": true
      }
    },
    {
      "input_query": "What was on channel 2?",
      "detected_missing": ["time_range"],
      "detected_present": ["channel"],
      "validation": {
        "correctly_identified": true,
        "prompt_quality": "Should ask for time range",
        "provides_examples": true
      }
    }
  ]
}
```

#### TC_2.1.2: 多重缺失信息识别
```json
{
  "test_id": "TC_2.1.2",
  "category": "Multiple Missing Info Detection",
  "test_cases": [
    {
      "input_query": "What topics were discussed?",
      "detected_missing": ["channel", "time_range"],
      "validation": {
        "identifies_all_missing": true,
        "prioritizes_prompts": true,
        "combined_prompt": "Should ask for both channel and time in one message"
      },
      "expected_prompt": {
        "structure": "list",
        "message": "To answer your question, I need:\n1. Which channel? (0, 1, 2, 3, or all)\n2. What time period? (e.g., last 10 minutes, past hour)",
        "suggestions": true
      }
    },
    {
      "input_query": "Tell me about it",
      "detected_missing": ["topic", "channel", "time_range"],
      "validation": {
        "too_vague": true,
        "helpful_guidance": "Should provide examples of proper queries"
      },
      "expected_prompt": {
        "message": "Your query is too vague. Here are some examples:",
        "examples": [
          "What was discussed on channel 0 in the last 10 minutes?",
          "Summarize all channels from the past hour",
          "What topics were covered on channel 2 between 10 and 20 minutes ago?"
        ]
      }
    }
  ]
}
```

### Test Case 2.2: 完成建议验证

#### TC_2.2.1: 建议质量检查
```json
{
  "test_id": "TC_2.2.1",
  "category": "Suggestion Quality",
  "test_cases": [
    {
      "input_query": "Summarize the last hour",
      "suggestions_provided": [
        "Summarize the last hour on channel 0",
        "Summarize the last hour on channel 1",
        "Summarize the last hour on channel 2",
        "Summarize the last hour on channel 3",
        "Summarize the last hour on all channels"
      ],
      "validation_criteria": {
        "completeness": "All suggestions are complete queries",
        "variety": "Provides multiple relevant options",
        "clickable": "Suggestions should be directly executable",
        "contextual": "Maintains original time context"
      }
    },
    {
      "input_query": "What happened on channel 2?",
      "suggestions_provided": [
        "What happened on channel 2 in the last 10 minutes?",
        "What happened on channel 2 in the past hour?",
        "What happened on channel 2 30 minutes ago?",
        "What happened on channel 2 between [time1] and [time2]?"
      ],
      "validation_criteria": {
        "time_variety": "Different time ranges offered",
        "maintains_channel": "All suggestions keep channel 2",
        "natural_language": "Phrasing sounds natural"
      }
    }
  ]
}
```

#### TC_2.2.2: 上下文感知建议
```json
{
  "test_id": "TC_2.2.2",
  "category": "Context-Aware Suggestions",
  "test_cases": [
    {
      "context": "User has been querying channel 0 frequently",
      "input_query": "What about the last 15 minutes?",
      "expected_behavior": {
        "infer_channel": true,
        "suggested_channel": 0,
        "confirmation_needed": true
      },
      "smart_suggestion": "What about the last 15 minutes on channel 0? (based on your recent queries)",
      "alternatives": [
        "What about the last 15 minutes on channel 1?",
        "What about the last 15 minutes on all channels?"
      ]
    },
    {
      "context": "Previous query was about 30 minutes ago",
      "input_query": "What about now?",
      "expected_behavior": {
        "infer_time_reference": true,
        "relative_to_previous": "From 30 minutes ago to now"
      },
      "smart_suggestion": "Show channel [X] from 30 minutes ago to now?"
    }
  ]
}
```

### Test Case 2.3: 可用选项显示

#### TC_2.3.1: 通道选项显示
```json
{
  "test_id": "TC_2.3.1",
  "category": "Channel Options Display",
  "test_cases": [
    {
      "scenario": "User asks without specifying channel",
      "input_query": "What's happening?",
      "expected_display": {
        "shows_available_channels": true,
        "channel_list": [0, 1, 2, 3],
        "includes_all_option": true,
        "format": "Available channels: 0, 1, 2, 3, or 'all channels'"
      },
      "additional_info": {
        "channel_descriptions": "Optional: brief description if available",
        "active_channels": "Highlight channels with recent activity"
      }
    }
  ]
}
```

#### TC_2.3.2: 时间选项显示
```json
{
  "test_id": "TC_2.3.2",
  "category": "Time Options Display",
  "test_cases": [
    {
      "scenario": "User asks without specifying time",
      "input_query": "Summarize channel 1",
      "expected_display": {
        "common_time_ranges": [
          "Last 5 minutes",
          "Last 10 minutes (default)",
          "Last 30 minutes",
          "Past hour",
          "Custom range"
        ],
        "shows_data_availability": true,
        "data_range_info": "Data available from [start_time] to now"
      }
    }
  ]
}
```

---

## 3. Test Auto-Correction（自动纠正测试）

### Test Case 3.1: 词序纠正

#### TC_3.1.1: 常见词序错误
```json
{
  "test_id": "TC_3.1.1",
  "category": "Word Order Correction",
  "test_cases": [
    {
      "input_query": "10 minutes last the channel 2 summarize",
      "corrected_query": "Summarize channel 2 from the last 10 minutes",
      "correction_steps": [
        "Identified keywords: summarize, channel 2, last 10 minutes",
        "Reordered to standard pattern: [action] [channel] [time]"
      ],
      "confidence": "high",
      "user_notification": "I understood your query as: 'Summarize channel 2 from the last 10 minutes'. Is this correct?"
    },
    {
      "input_query": "channel 0 on 15 minutes ago what was",
      "corrected_query": "What was on channel 0 15 minutes ago?",
      "correction_steps": [
        "Identified: what was, channel 0, 15 minutes ago",
        "Reconstructed question format"
      ],
      "user_notification": "Corrected to: 'What was on channel 0 15 minutes ago?'"
    },
    {
      "input_query": "from hour past the all channels summarize",
      "corrected_query": "Summarize all channels from the past hour",
      "correction_steps": [
        "Parsed: summarize, all channels, past hour",
        "Applied standard syntax"
      ]
    }
  ]
}
```

#### TC_3.1.2: 部分正确的词序
```json
{
  "test_id": "TC_3.1.2",
  "category": "Partial Word Order Issues",
  "test_cases": [
    {
      "input_query": "Summarize from last 10 minutes channel 2",
      "corrected_query": "Summarize channel 2 from the last 10 minutes",
      "issue": "Channel identifier misplaced",
      "auto_fix": true
    },
    {
      "input_query": "What on channel 0 was the last hour?",
      "corrected_query": "What was on channel 0 in the last hour?",
      "issue": "Missing 'was' and wrong preposition",
      "auto_fix": true
    }
  ]
}
```

### Test Case 3.2: 自动纠正能力验证

#### TC_3.2.1: 纠正置信度测试
```json
{
  "test_id": "TC_3.2.1",
  "category": "Correction Confidence",
  "test_cases": [
    {
      "input_query": "Summarize chanel 0 from last 10 minuts",
      "corrections": {
        "chanel → channel": {"confidence": "high", "certainty": 0.95},
        "minuts → minutes": {"confidence": "high", "certainty": 0.98}
      },
      "auto_apply": true,
      "user_notification": "Auto-corrected spelling errors"
    },
    {
      "input_query": "Show me chan 2",
      "corrections": {
        "chan": {
          "possibilities": ["channel 2", "chain 2"],
          "best_guess": "channel 2",
          "confidence": "medium",
          "certainty": 0.75
        }
      },
      "auto_apply": true,
      "user_notification": "Did you mean 'channel 2'? (auto-applied)"
    },
    {
      "input_query": "Summarize fan 1",
      "corrections": {
        "fan": {
          "possibilities": ["channel", "can"],
          "best_guess": "channel 1",
          "confidence": "low",
          "certainty": 0.6
        }
      },
      "auto_apply": false,
      "user_notification": "Did you mean 'channel 1'? If yes, click here."
    }
  ]
}
```

#### TC_3.2.2: 多重纠正
```json
{
  "test_id": "TC_3.2.2",
  "category": "Multiple Corrections",
  "test_cases": [
    {
      "input_query": "Summerize channal 0 from last our",
      "corrections": [
        {"Summerize → Summarize": "spelling"},
        {"channal → channel": "spelling"},
        {"our → hour": "spelling"}
      ],
      "corrected_query": "Summarize channel 0 from last hour",
      "show_corrections": true,
      "user_message": "Auto-corrected 3 spelling errors: Summerize→Summarize, channal→channel, our→hour"
    },
    {
      "input_query": "10 minits ago chanle 2 what",
      "corrections": [
        {"minits → minutes": "spelling"},
        {"chanle → channel": "spelling"},
        {"word order": "syntax"}
      ],
      "corrected_query": "What was on channel 2 10 minutes ago?",
      "complex_correction": true
    }
  ]
}
```

### Test Case 3.3: 纠正后查询执行

#### TC_3.3.1: 自动执行纠正查询
```json
{
  "test_id": "TC_3.3.1",
  "category": "Execute Corrected Query",
  "test_cases": [
    {
      "input_query": "Summarize chanel 0 last 10 min",
      "auto_correction": "Summarize channel 0 from the last 10 minutes",
      "execution": {
        "auto_execute": true,
        "show_what_was_corrected": true,
        "allow_undo": true
      },
      "user_experience": {
        "notification": "Executed: 'Summarize channel 0 from the last 10 minutes' (auto-corrected)",
        "undo_option": "Not what you meant? Click here to rephrase"
      }
    },
    {
      "input_query": "channel 0 on 15 minutes ago what was",
      "auto_correction": "What was on channel 0 15 minutes ago?",
      "execution": {
        "confirmation_needed": false,
        "confidence_threshold": 0.8,
        "auto_execute": true
      }
    }
  ]
}
```

#### TC_3.3.2: 确认后执行
```json
{
  "test_id": "TC_3.3.2",
  "category": "Confirm Before Execute",
  "test_cases": [
    {
      "input_query": "Show me fan 1 stuff",
      "auto_correction": "Show me channel 1 from the last 10 minutes",
      "execution": {
        "auto_execute": false,
        "confidence_threshold": 0.6,
        "requires_confirmation": true
      },
      "user_prompt": {
        "message": "Did you mean: 'Show me channel 1 from the last 10 minutes'?",
        "options": ["Yes, execute this", "No, let me rephrase"],
        "allow_edit": true
      }
    }
  ]
}
```

---

## 4. Validate Error Messages（错误消息验证）

### Test Case 4.1: 错误消息对比（改进前后）

#### TC_4.1.1: 通道错误消息
```json
{
  "test_id": "TC_4.1.1",
  "category": "Channel Error Messages - Before/After",
  "test_cases": [
    {
      "input_query": "Summarize channel 5 from the last 10 minutes",
      "before_improvement": {
        "error_message": "Error: Invalid channel",
        "helpful": false,
        "actionable": false,
        "user_friendly": false
      },
      "after_improvement": {
        "error_message": "Channel 5 is not available",
        "details": "Available channels: 0, 1, 2, 3",
        "suggestions": [
          "Did you mean channel 3?",
          "Or search all channels?"
        ],
        "helpful": true,
        "actionable": true,
        "user_friendly": true
      },
      "improvement_metrics": {
        "clarity": "+80%",
        "actionability": "+100%",
        "user_satisfaction": "expected to improve"
      }
    },
    {
      "input_query": "What was on channel -1?",
      "before_improvement": {
        "error_message": "Invalid input",
        "technical": true
      },
      "after_improvement": {
        "error_message": "Channel -1 is not valid",
        "explanation": "Channel numbers must be between 0 and 3",
        "suggestion": "Please try: channel 0, 1, 2, or 3"
      }
    }
  ]
}
```

#### TC_4.1.2: 时间错误消息
```json
{
  "test_id": "TC_4.1.2",
  "category": "Time Error Messages - Before/After",
  "test_cases": [
    {
      "input_query": "What was at 25:00 on channel 0?",
      "before_improvement": {
        "error_message": "Parse error: invalid time",
        "shows_stack_trace": false,
        "helpful": false
      },
      "after_improvement": {
        "error_message": "Invalid time: 25:00",
        "explanation": "Hours must be 0-23 for 24-hour format, or 1-12 with AM/PM",
        "examples": [
          "Use '13:00' for 1 PM",
          "Or '1:00 PM'",
          "Or '01:00' for 1 AM"
        ],
        "suggestion": "Did you mean 01:00 (1 AM)?"
      }
    },
    {
      "input_query": "Summarize from 5pm to 3pm on channel 1",
      "before_improvement": {
        "error_message": "Error in time range",
        "vague": true
      },
      "after_improvement": {
        "error_message": "Invalid time range: end time (3pm) is before start time (5pm)",
        "suggestion": "Did you mean from 3pm to 5pm?",
        "auto_fix_option": "Click to swap times"
      }
    }
  ]
}
```

#### TC_4.1.3: 格式错误消息
```json
{
  "test_id": "TC_4.1.3",
  "category": "Format Error Messages - Before/After",
  "test_cases": [
    {
      "input_query": "akljsdflkj channel 0",
      "before_improvement": {
        "error_message": "Unable to process query",
        "generic": true
      },
      "after_improvement": {
        "error_message": "I couldn't understand your query",
        "guidance": "Try using this format:",
        "examples": [
          "'Summarize channel 0 from the last 10 minutes'",
          "'What was on channel 1 15 minutes ago?'",
          "'Show me channel 2 from the past hour'"
        ],
        "help_link": "View more examples"
      }
    }
  ]
}
```

### Test Case 4.2: 具体修复建议

#### TC_4.2.1: 建议的具体性
```json
{
  "test_id": "TC_4.2.1",
  "category": "Suggestion Specificity",
  "test_cases": [
    {
      "error_type": "missing_channel",
      "generic_suggestion": "Please specify a channel",
      "specific_suggestion": {
        "message": "Which channel would you like to query?",
        "options": ["Channel 0", "Channel 1", "Channel 2", "Channel 3", "All channels"],
        "clickable": true
      },
      "specificity_score": 9/10
    },
    {
      "error_type": "invalid_time_format",
      "generic_suggestion": "Use correct time format",
      "specific_suggestion": {
        "message": "Please use one of these time formats:",
        "formats": [
          "Relative: 'last 10 minutes', 'past hour', '15 minutes ago'",
          "Absolute: '2:00 PM', '14:30', '9 o'clock'",
          "Range: 'between 10 and 20 minutes ago'"
        ],
        "examples": true
      },
      "specificity_score": 10/10
    },
    {
      "error_type": "query_too_vague",
      "generic_suggestion": "Be more specific",
      "specific_suggestion": {
        "message": "Your query needs more details. A complete query includes:",
        "required_elements": [
          "1. Which channel? (or 'all channels')",
          "2. What time period? (e.g., 'last 10 minutes')",
          "3. What action? (summarize, show, what was discussed)"
        ],
        "example": "Try: 'Summarize channel 0 from the last 10 minutes'"
      },
      "specificity_score": 10/10
    }
  ]
}
```

#### TC_4.2.2: 可操作建议
```json
{
  "test_id": "TC_4.2.2",
  "category": "Actionable Suggestions",
  "test_cases": [
    {
      "input_query": "Summarize the last 10 minutes",
      "suggestion": {
        "type": "clickable_options",
        "message": "Select a channel:",
        "options": [
          {"text": "Channel 0", "action": "execute_with_channel_0"},
          {"text": "Channel 1", "action": "execute_with_channel_1"},
          {"text": "Channel 2", "action": "execute_with_channel_2"},
          {"text": "Channel 3", "action": "execute_with_channel_3"},
          {"text": "All channels", "action": "execute_with_all_channels"}
        ],
        "one_click_fix": true
      }
    },
    {
      "input_query": "What was on channel 0 at 25:00?",
      "suggestion": {
        "type": "auto_fix_button",
        "message": "Invalid time. Did you mean 01:00?",
        "action_button": {
          "text": "Yes, search at 01:00",
          "action": "execute_with_corrected_time"
        },
        "alternative": {
          "text": "No, let me specify a different time",
          "action": "open_time_picker"
        }
      }
    }
  ]
}
```

### Test Case 4.3: 示例格式指导

#### TC_4.3.1: 格式示例质量
```json
{
  "test_id": "TC_4.3.1",
  "category": "Example Format Quality",
  "validation_criteria": {
    "variety": "Shows different query patterns",
    "completeness": "All examples are complete queries",
    "relevance": "Examples relate to user's attempted query",
    "copy_paste_ready": "Can be used directly",
    "progressive_complexity": "From simple to advanced"
  },
  "example_set": {
    "basic_queries": [
      "Summarize channel 0 from the last 10 minutes",
      "What was on channel 1 in the past hour?",
      "Show me channel 2 from the last 30 minutes"
    ],
    "intermediate_queries": [
      "What was discussed on channel 0 15 minutes ago?",
      "Summarize all channels from the past hour",
      "What topics were covered on channel 2 between 10 and 20 minutes ago?"
    ],
    "advanced_queries": [
      "At 2:00 PM, what was the topic on channel 3, using a 10 minute window?",
      "Summarize the main topics on channel 0, excluding the past 5 minutes",
      "Between 9 AM and 10 AM, what was discussed on channel 1?"
    ]
  }
}
```

#### TC_4.3.2: 上下文相关示例
```json
{
  "test_id": "TC_4.3.2",
  "category": "Context-Relevant Examples",
  "test_cases": [
    {
      "user_error": "Missing channel",
      "examples_shown": [
        "✓ Summarize channel 0 from the last 10 minutes",
        "✓ What was on channel 1 in the past hour?",
        "✗ Summarize the last 10 minutes  ← missing channel"
      ],
      "highlights_fix": true
    },
    {
      "user_error": "Missing time",
      "examples_shown": [
        "✓ What was on channel 0 in the last 10 minutes?",
        "✓ Summarize channel 1 from 15 minutes ago",
        "✗ What was on channel 0?  ← missing time"
      ]
    },
    {
      "user_error": "Wrong word order",
      "examples_shown": [
        "✓ Summarize channel 0 from the last 10 minutes",
        "✗ 10 minutes last the channel 0 summarize  ← wrong order",
        "Shows proper order: [Action] [Channel] [Time]"
      ]
    }
  ]
}
```

---

## 5. Test Edge Cases（边缘案例测试）

### Test Case 5.1: 完全模糊的查询

#### TC_5.1.1: 极度简短的查询
```json
{
  "test_id": "TC_5.1.1",
  "category": "Extremely Short Queries",
  "test_cases": [
    {
      "input_query": "what?",
      "response": {
        "type": "educational_prompt",
        "message": "I can help you search through radio transcripts! Try asking:",
        "examples": [
          "What was discussed on channel 0 in the last 10 minutes?",
          "Summarize channel 1 from the past hour",
          "What topics were covered recently?"
        ],
        "help_text": "Include: which channel and what time period you're interested in"
      }
    },
    {
      "input_query": "show",
      "response": {
        "message": "What would you like me to show? For example:",
        "suggestions": [
          "Show channel 0 from the last 10 minutes",
          "Show transcripts from the past hour",
          "Show all recent activity"
        ]
      }
    },
    {
      "input_query": "0",
      "response": {
        "interpretation": "Possibly referring to channel 0",
        "clarification": "Did you want information about channel 0?",
        "follow_up": "What time period would you like to search?"
      }
    }
  ]
}
```

#### TC_5.1.2: 无意义输入
```json
{
  "test_id": "TC_5.1.2",
  "category": "Nonsensical Input",
  "test_cases": [
    {
      "input_query": "asdfghjkl",
      "response": {
        "type": "gentle_error",
        "message": "I couldn't understand that. Let me help you get started:",
        "guide": {
          "basic_format": "Try: [action] channel [number] from [time period]",
          "examples": [
            "Summarize channel 0 from the last 10 minutes",
            "What was on channel 1 in the past hour?"
          ]
        },
        "not_harsh": true
      }
    },
    {
      "input_query": "12345 !@#$%",
      "response": {
        "message": "That doesn't look like a valid query. Here's how to search:",
        "tutorial": "Brief tutorial on query format",
        "helpful": true
      }
    }
  ]
}
```

#### TC_5.1.3: 多语言或混合输入
```json
{
  "test_id": "TC_5.1.3",
  "category": "Non-English or Mixed Input",
  "test_cases": [
    {
      "input_query": "总结 channel 0",
      "response": {
        "detected_language": "mixed (Chinese + English)",
        "message": "I detected a mixed language query. I work best with English. Try:",
        "translation_hint": "'总结' might mean 'summarize'",
        "suggestion": "Summarize channel 0 from the last 10 minutes?"
      }
    },
    {
      "input_query": "Résumé canal 0",
      "response": {
        "detected_language": "French",
        "message": "I work in English. Did you mean:",
        "suggestion": "Summarize channel 0?"
      }
    }
  ]
}
```

### Test Case 5.2: 用户引导能力测试

#### TC_5.2.1: 渐进式引导
```json
{
  "test_id": "TC_5.2.1",
  "category": "Progressive Guidance",
  "interaction_flow": [
    {
      "step": 1,
      "user_input": "I want to know",
      "system_response": {
        "message": "What would you like to know?",
        "guidance": "I can help you find information from radio channels. You can ask about:",
        "topics": [
          "Recent discussions on specific channels",
          "Topics covered in a time period",
          "Summaries of channel content"
        ]
      }
    },
    {
      "step": 2,
      "user_input": "Recent discussions",
      "system_response": {
        "message": "Great! Which channel would you like to check?",
        "options": ["Channel 0", "Channel 1", "Channel 2", "Channel 3", "All channels"]
      }
    },
    {
      "step": 3,
      "user_input": "Channel 0",
      "system_response": {
        "message": "Perfect! How far back would you like to search?",
        "time_options": [
          "Last 5 minutes",
          "Last 10 minutes",
          "Last 30 minutes",
          "Past hour",
          "Custom time"
        ]
      }
    },
    {
      "step": 4,
      "user_input": "Last 10 minutes",
      "system_response": {
        "message": "Got it! Searching channel 0 from the last 10 minutes...",
        "final_query": "Summarize channel 0 from the last 10 minutes",
        "executes": true
      }
    }
  ],
  "validation": {
    "patient_guidance": true,
    "never_refuses": true,
    "educational": true,
    "completion_rate": "should reach valid query"
  }
}
```

#### TC_5.2.2: 新用户教育
```json
{
  "test_id": "TC_5.2.2",
  "category": "First-Time User Education",
  "scenarios": [
    {
      "user_type": "first_time",
      "trigger": "vague or incomplete query",
      "response": {
        "welcome": "Welcome! Let me help you get started.",
        "explanation": "This system lets you search through radio channel transcripts.",
        "tutorial": {
          "components": [
            "1. Choose a channel (0-3) or search all",
            "2. Specify a time period (e.g., last 10 minutes)",
            "3. Ask your question"
          ],
          "interactive": true
        },
        "first_query_help": {
          "template": "Try this template: Summarize channel [X] from [time]",
          "fill_in_blanks": true
        }
      }
    },
    {
      "user_type": "returning_confused",
      "trigger": "errors after previous successful queries",
      "response": {
        "reminder": "Here's a quick reminder of the query format:",
        "reference_previous": "You've previously asked: '[previous_successful_query]'",
        "pattern_hint": "Follow a similar pattern"
      }
    }
  ]
}
```

#### TC_5.2.3: 持续支持
```json
{
  "test_id": "TC_5.2.3",
  "category": "Continuous User Support",
  "features": [
    {
      "feature": "Help command",
      "trigger": "User types 'help'",
      "response": {
        "quick_reference": true,
        "examples": true,
        "tips": [
          "You can ask about any channel (0-3)",
          "Time periods can be relative (last 10 minutes) or absolute (at 2 PM)",
          "Use 'excluding channel X' to filter results"
        ]
      }
    },
    {
      "feature": "Examples command",
      "trigger": "User types 'examples' or 'show examples'",
      "response": {
        "categorized_examples": {
          "recent_summaries": [...],
          "specific_times": [...],
          "time_ranges": [...],
          "advanced": [...]
        }
      }
    },
    {
      "feature": "Contextual help",
      "trigger": "Repeated errors",
      "response": {
        "message": "I notice you're having trouble. Would you like:",
        "options": [
          "See example queries",
          "Step-by-step query builder",
          "Start over with guidance"
        ]
      }
    }
  ]
}
```

### Test Case 5.3: 歧义处理

#### TC_5.3.1: 可能有多种解释的查询
```json
{
  "test_id": "TC_5.3.1",
  "category": "Ambiguous Queries",
  "test_cases": [
    {
      "input_query": "What happened at 2?",
      "ambiguities": [
        "Channel 2 or 2 o'clock?",
        "2 minutes ago or 2:00 PM?"
      ],
      "response": {
        "type": "clarification_prompt",
        "message": "Did you mean:",
        "options": [
          "What happened on channel 2? (which time period?)",
          "What happened at 2:00 PM? (which channel?)",
          "What happened at 2:00 AM? (which channel?)",
          "What happened 2 minutes ago? (which channel?)"
        ],
        "allows_selection": true
      }
    },
    {
      "input_query": "Show me 1",
      "ambiguities": ["Channel 1 or 1 o'clock or 1 minute ago?"],
      "response": {
        "best_guess": "Channel 1 (most likely)",
        "confirmation": "Showing channel 1. Is this what you wanted?",
        "alternatives": "If you meant 1 o'clock or 1 minute ago, click here"
      }
    }
  ]
}
```

#### TC_5.3.2: 冲突信息处理
```json
{
  "test_id": "TC_5.3.2",
  "category": "Conflicting Information",
  "test_cases": [
    {
      "input_query": "Summarize channel 0 and channel 1 from channel 2",
      "conflict": "Multiple channels mentioned",
      "response": {
        "message": "I'm not sure which channel you want. Did you mean:",
        "options": [
          "Summarize channels 0, 1, and 2",
          "Summarize channel 0",
          "Summarize channel 1",
          "Summarize channel 2"
        ]
      }
    },
    {
      "input_query": "What was 10 minutes ago from the last hour?",
      "conflict": "Conflicting time specifications",
      "response": {
        "message": "The time specification is unclear. Did you mean:",
        "options": [
          "10 minutes ago (specific time)",
          "The last hour (time range)",
          "From 1 hour ago to 10 minutes ago (range)"
        ]
      }
    }
  ]
}
```

---

## 6. 综合测试场景

### Test Case 6.1: 真实用户行为模拟

#### TC_6.1.1: 新手用户场景
```json
{
  "test_id": "TC_6.1.1",
  "scenario": "Complete beginner",
  "user_journey": [
    {
      "query": "tell me what's happening",
      "expected": "Educational response with guidance",
      "system_helps": true
    },
    {
      "query": "ok channel 0",
      "expected": "Recognizes channel, asks for time",
      "system_builds_on_input": true
    },
    {
      "query": "now",
      "expected": "Interprets as 'recent' with default window",
      "executes_query": true
    }
  ],
  "success_criteria": {
    "user_reaches_valid_query": true,
    "frustration_minimized": true,
    "learns_correct_format": true
  }
}
```

#### TC_6.1.2: 匆忙用户场景
```json
{
  "test_id": "TC_6.1.2",
  "scenario": "User in a hurry, types quickly with errors",
  "user_journey": [
    {
      "query": "summare chan 0 last 10 mins",
      "expected": "Auto-corrects and executes immediately",
      "user_notification": "Auto-corrected: 'Summarize channel 0 last 10 minutes'",
      "no_delay": true
    }
  ],
  "success_criteria": {
    "immediate_execution": true,
    "corrections_transparent": true,
    "user_not_blocked": true
  }
}
```

### Test Case 6.2: 压力测试

#### TC_6.2.1: 连续错误查询
```json
{
  "test_id": "TC_6.2.1",
  "scenario": "Multiple errors in sequence",
  "query_sequence": [
    "what",
    "channel",
    "0",
    "summarize",
    "last 10"
  ],
  "expected_behavior": {
    "patient_guidance": "System continues to help",
    "progressive_building": "Recognizes user is building up a query",
    "suggestion_evolution": "Suggestions get more specific",
    "completion_offered": "After 'last 10', suggests 'last 10 minutes'"
  }
}
```

#### TC_6.2.2: 快速切换上下文
```json
{
  "test_id": "TC_6.2.2",
  "scenario": "Rapid context switches",
  "query_sequence": [
    "channel 0 last 10 minutes",
    "no wait channel 1",
    "actually 15 minutes",
    "change to channel 2"
  ],
  "expected_behavior": {
    "tracks_modifications": true,
    "applies_latest_context": true,
    "final_query": "Summarize channel 2 from the last 15 minutes"
  }
}
```

---

## 7. 性能与可用性指标

### 测试指标

```json
{
  "response_quality_metrics": {
    "error_recovery_rate": {
      "target": "> 90%",
      "measurement": "% of errors that result in successful query"
    },
    "auto_correction_accuracy": {
      "target": "> 85%",
      "measurement": "% of auto-corrections that are correct"
    },
    "user_satisfaction": {
      "target": "> 4.0/5.0",
      "measurement": "User rating of error message helpfulness"
    },
    "time_to_valid_query": {
      "target": "< 30 seconds",
      "measurement": "Time from first error to successful query"
    }
  },
  "technical_metrics": {
    "correction_response_time": {
      "target": "< 200ms",
      "measurement": "Time to provide suggestions/corrections"
    },
    "false_positive_rate": {
      "target": "< 5%",
      "measurement": "% of correct queries flagged as errors"
    }
  }
}
```

---

## 8. 测试执行清单

### 准备工作
- [ ] 系统已部署并运行
- [ ] 记录当前错误处理行为（作为基线）
- [ ] 准备测试查询列表
- [ ] 设置监控和日志记录

### 执行测试
- [ ] Test 1: 查询解析测试
  - [ ] 1.1: 缺少通道号
  - [ ] 1.2: 缺少时间信息
  - [ ] 1.3: 格式错误
- [ ] Test 2: 智能提示验证
  - [ ] 2.1: 识别缺失信息
  - [ ] 2.2: 完成建议质量
  - [ ] 2.3: 可用选项显示
- [ ] Test 3: 自动纠正测试
  - [ ] 3.1: 词序纠正
  - [ ] 3.2: 纠正能力验证
  - [ ] 3.3: 纠正后执行
- [ ] Test 4: 错误消息验证
  - [ ] 4.1: 改进前后对比
  - [ ] 4.2: 具体修复建议
  - [ ] 4.3: 示例格式指导
- [ ] Test 5: 边缘案例
  - [ ] 5.1: 完全模糊查询
  - [ ] 5.2: 用户引导能力
  - [ ] 5.3: 歧义处理

### 结果记录
- [ ] 记录所有测试结果
- [ ] 对比改进前后的表现
- [ ] 收集用户反馈
- [ ] 生成改进建议报告

---

## 9. 成功标准

### 必须满足（Must Have）
- ✅ 90%+ 的不完整查询能得到有效提示
- ✅ 85%+ 的拼写错误能被自动纠正
- ✅ 100% 的错误消息包含可操作建议
- ✅ 无技术术语暴露给用户

### 应该满足（Should Have）
- ✅ 上下文感知的建议
- ✅ 一键修复常见错误
- ✅ 渐进式用户引导
- ✅ 多语言查询的优雅降级

### 可以满足（Could Have）
- ⭕ 学习用户查询模式
- ⭕ 个性化建议
- ⭕ 自然语言对话式交互
- ⭕ 语音输入支持

---

## 10. 参考资料

### 最佳实践
- 错误消息应说明"什么出错了"和"如何修复"
- 提供具体示例而非抽象指导
- 自动修复明显错误，确认不确定的修复
- 永远不让用户陷入死胡同

### 用户体验原则
1. **Be Helpful**: 提供解决方案，不只是指出问题
2. **Be Clear**: 使用简单明了的语言
3. **Be Specific**: 给出具体的修复建议
4. **Be Forgiving**: 容忍多种输入格式
5. **Be Educational**: 帮助用户学习正确格式

### 技术实现建议
- 使用 NLP 进行智能查询解析
- 实现模糊匹配算法
- 构建常见错误模式库
- 提供交互式查询构建器
- 记录和学习用户查询模式

---

## 附录：测试数据集

### 常见错误查询库
```json
{
  "missing_channel": [
    "Summarize the last 10 minutes",
    "What was discussed recently?",
    "Show me transcripts"
  ],
  "missing_time": [
    "What was on channel 0?",
    "Summarize channel 1",
    "Show channel 2"
  ],
  "typos": [
    "Summerize channal 0",
    "What happend on chanel 1?",
    "Show me rescent data"
  ],
  "wrong_order": [
    "10 minutes last channel 0",
    "channel 1 on what was",
    "from hour past all channels"
  ],
  "invalid_values": [
    "channel 5",
    "channel -1",
    "at 25:00",
    "last -10 minutes"
  ]
}
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-08  
**相关项目**: https://github.com/NVIDIA-AI-Blueprints/streaming-data-to-rag
