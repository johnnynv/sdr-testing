#!/usr/bin/env python3
"""
RAG 系统错误处理与智能提示 UI 自动化测试
REQ-02: 查询错误处理增强
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page


@dataclass
class TestResult:
    test_id: str
    category: str
    query: str
    success: bool
    has_response: bool
    response_helpful: bool
    response_time_ms: float
    response_text: Optional[str] = None
    error_message: Optional[str] = None


class RAGErrorHandlingTester:
    def __init__(self, ui_url: str = "http://localhost:3000", headless: bool = False, enable_screenshots: bool = True):
        self.ui_url = ui_url
        self.headless = headless
        self.enable_screenshots = enable_screenshots
        self.results: List[TestResult] = []
    
    def execute_query(self, page: Page, query: str, screenshot: bool = True) -> tuple[bool, bool, float, str]:
        """执行查询，返回(是否成功, 响应是否有帮助, 响应时间, 响应文本)"""
        start_time = time.time()
        
        try:
            print(f"    ⏳ 准备输入查询...")
            
            # 查找输入框（不刷新页面，保留对话历史）
            print(f"    ⏳ 查找输入框...")
            input_box = page.locator('textarea, input[type="text"]').first
            input_box.wait_for(state='visible', timeout=5000)
            print(f"    ✓ 找到输入框")
            
            # 清空并输入查询
            print(f"    ⏳ 输入查询: {query[:50]}...")
            input_box.clear()
            page.wait_for_timeout(500)
            
            # 使用 type 方法逐字符输入，更接近真实用户行为
            input_box.type(query, delay=20)  # 每个字符间隔20ms
            page.wait_for_timeout(1000)  # 等待输入完成和UI更新
            
            # 验证输入
            current_value = input_box.input_value()
            if current_value == query:
                print(f"    ✓ 查询已输入（{len(query)} 字符）")
            else:
                print(f"    ⚠️  输入验证失败（期望: {len(query)} 字符，实际: {len(current_value)} 字符），重试...")
                input_box.clear()
                page.wait_for_timeout(500)
                input_box.type(query, delay=20)
                page.wait_for_timeout(1000)
            
            # 确保输入框聚焦，内容可见
            input_box.focus()
            page.wait_for_timeout(800)  # 额外等待确保渲染完成
            
            # 截图1: 输入后、提交前
            if screenshot and self.enable_screenshots:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"screenshots/error_input_{timestamp}.png"
                import os
                os.makedirs("screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    📸 截图（输入后）: {screenshot_path}")
                
                # 验证截图文件大小
                import os
                size = os.path.getsize(screenshot_path)
                print(f"       文件大小: {size/1024:.1f} KB")
            
            # 提交查询
            print(f"    ⏳ 提交查询...")
            input_box.press('Enter')
            print(f"    ✓ 查询已提交")
            
            # 等待"Thinking"消失
            print(f"    ⏳ 等待AI响应（最多40秒）...")
            response_started = False
            for i in range(40):
                page.wait_for_timeout(1000)
                body_text = page.inner_text('body')
                if 'Thinking' not in body_text and 'Stop Generating' not in body_text:
                    print(f"    ✓ 响应已生成（{i+1}秒）")
                    response_started = True
                    break
                if i % 5 == 4:
                    print(f"       ...处理中 ({i+1}秒)")
            
            if not response_started:
                print(f"    ⚠️  响应超时")
            
            # 再等待2秒确保渲染完成
            page.wait_for_timeout(2000)
            
            # 截图2: 响应后
            if screenshot and self.enable_screenshots:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"screenshots/error_response_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    📸 截图（响应后）: {screenshot_path}")
                
                import os
                size = os.path.getsize(screenshot_path)
                print(f"       文件大小: {size/1024:.1f} KB")
            
            # 获取最新响应 - 使用JavaScript方法（最可靠）
            print(f"    ⏳ 提取响应内容...")
            response_text = ""
            
            # 使用JavaScript获取body文本
            full_body_text = page.evaluate('() => document.body.innerText')
            print(f"       Body文本长度: {len(full_body_text)} 字符")
            query_pos = full_body_text.find(query)
            print(f"       查询位置: {query_pos if query_pos >= 0 else '未找到'}")
            
            if query_pos >= 0:
                # 提取查询之后的文本
                after_query = full_body_text[query_pos + len(query):]
                after_query = after_query.strip()
                
                # 查找响应结束标记
                end_markers = ['Regenerate response', 'Stop Generating', '\n\n\n']
                end_pos = len(after_query)
                for marker in end_markers:
                    marker_pos = after_query.find(marker)
                    if marker_pos > 0 and marker_pos < end_pos:
                        end_pos = marker_pos
                
                response_text = after_query[:end_pos].strip()
                
                if response_text and response_text != query and len(response_text) > 10:
                    print(f"    ✓ AI响应（{len(response_text)} 字符）: {response_text[:100]}...")
                else:
                    print(f"    ⚠️  响应为空或无效")
            else:
                print(f"    ⚠️  未在页面中找到查询文本")
            
            # 判断响应是否有帮助（包含建议、示例等）
            helpful_keywords = ['suggest', 'try', 'example', 'available', 'channel', 'time']
            is_helpful = any(kw in response_text.lower() for kw in helpful_keywords)
            if is_helpful:
                print(f"    ✓ 响应包含有用建议")
            
            elapsed = (time.time() - start_time) * 1000
            return True, is_helpful, elapsed, response_text
            
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
            elapsed = (time.time() - start_time) * 1000
            return False, False, elapsed, str(e)
    
    def run_tests(self):
        """执行所有测试"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(self.ui_url, timeout=60000)  # 60秒超时
            page.wait_for_load_state('domcontentloaded')  # 等待 DOM 加载即可
            
            print(f"\n{'='*60}\nRAG 错误处理与智能提示测试\n访问: {self.ui_url}\n{'='*60}")
            
            self.test_missing_channel(page)
            self.test_missing_time(page)
            self.test_format_errors(page)
            self.test_invalid_values(page)
            self.test_vague_queries(page)
            
            browser.close()
        
        self.generate_report()
    
    def test_missing_channel(self, page: Page):
        """测试缺少通道号"""
        print(f"\n{'='*60}\n测试 1: 缺少通道号\n{'='*60}")
        
        tests = [
            ("TC_1.1", "完全缺少", "Summarize the last 10 minutes"),
            ("TC_1.2", "缺少，多信息", "What topics were discussed in the past hour?"),
            ("TC_1.3", "非常模糊", "Show me recent transcripts"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            success, helpful, elapsed, text = self.execute_query(page, query)
            
            result = TestResult(
                test_id=test_id,
                category="Missing Channel",
                query=query,
                success=success,
                has_response=success,
                response_helpful=helpful,
                response_time_ms=elapsed,
                response_text=text[:200] if text else None
            )
            self.results.append(result)
            
            print(f"  结果: 响应={'✓' if success else '✗'} | 有帮助={'✓' if helpful else '✗'} | {elapsed:.0f}ms")
            print(f"  -" * 30)
    
    def test_missing_time(self, page: Page):
        """测试缺少时间信息"""
        print(f"\n{'='*60}\n测试 2: 缺少时间信息\n{'='*60}")
        
        tests = [
            ("TC_2.1", "缺时间", "What was discussed on channel 0?"),
            ("TC_2.2", "仅通道", "Summarize channel 2"),
            ("TC_2.3", "模糊时间", "What was discussed on channel 1 recently?"),
            ("TC_2.4", "非常模糊", "Show me old transcripts from channel 2"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            success, helpful, elapsed, text = self.execute_query(page, query)
            
            result = TestResult(
                test_id=test_id,
                category="Missing Time",
                query=query,
                success=success,
                has_response=success,
                response_helpful=helpful,
                response_time_ms=elapsed,
                response_text=text[:200] if text else None
            )
            self.results.append(result)
            
            print(f"  结果: 响应={'✓' if success else '✗'} | 有帮助={'✓' if helpful else '✗'} | {elapsed:.0f}ms")
            print(f"  -" * 30)
    
    def test_format_errors(self, page: Page):
        """测试格式错误"""
        print(f"\n{'='*60}\n测试 3: 格式错误\n{'='*60}")
        
        tests = [
            ("TC_3.1", "词序错误", "channel 0 what last 10 minutes"),
            ("TC_3.2", "拼写错误", "Summerize channal 0 from last our"),
            ("TC_3.3", "缩写", "What happened on ch 3 recently?"),
            ("TC_3.4", "错误术语", "What was discussed on stream 2 in the past hour?"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            success, helpful, elapsed, text = self.execute_query(page, query)
            
            result = TestResult(
                test_id=test_id,
                category="Format Error",
                query=query,
                success=success,
                has_response=success,
                response_helpful=helpful,
                response_time_ms=elapsed,
                response_text=text[:200] if text else None
            )
            self.results.append(result)
            
            # 格式错误应该被自动纠正或给出建议
            print(f"  结果: 响应={'✓' if success else '✗'} | 纠正/建议={'✓' if helpful else '✗'} | {elapsed:.0f}ms")
            print(f"  -" * 30)
    
    def test_invalid_values(self, page: Page):
        """测试无效值"""
        print(f"\n{'='*60}\n测试 4: 无效值\n{'='*60}")
        
        tests = [
            ("TC_4.1", "无效通道", "Summarize channel 5 from the last 10 minutes"),
            ("TC_4.2", "负通道", "What was on channel -1 fifteen minutes ago?"),
            ("TC_4.3", "无效时间", "What was discussed at 25:00 on channel 0?"),
            ("TC_4.4", "负时间", "Summarize the last -10 minutes on channel 0"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            success, helpful, elapsed, text = self.execute_query(page, query)
            
            result = TestResult(
                test_id=test_id,
                category="Invalid Value",
                query=query,
                success=success,
                has_response=success,
                response_helpful=helpful,
                response_time_ms=elapsed,
                response_text=text[:200] if text else None
            )
            self.results.append(result)
            
            # 无效值应该有清晰的错误提示
            print(f"  结果: 响应={'✓' if success else '✗'} | 错误说明={'✓' if helpful else '✗'} | {elapsed:.0f}ms")
            print(f"  -" * 30)
    
    def test_vague_queries(self, page: Page):
        """测试极度模糊的查询"""
        print(f"\n{'='*60}\n测试 5: 极度模糊的查询\n{'='*60}")
        
        tests = [
            ("TC_5.1", "极短", "what?"),
            ("TC_5.2", "单词", "show"),
            ("TC_5.3", "数字", "0"),
            ("TC_5.4", "乱码", "asdfghjkl"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            success, helpful, elapsed, text = self.execute_query(page, query)
            
            result = TestResult(
                test_id=test_id,
                category="Vague Query",
                query=query,
                success=success,
                has_response=success,
                response_helpful=helpful,
                response_time_ms=elapsed,
                response_text=text[:200] if text else None
            )
            self.results.append(result)
            
            # 模糊查询应该得到友好的引导
            print(f"  结果: 响应={'✓' if success else '✗'} | 引导={'✓' if helpful else '✗'} | {elapsed:.0f}ms")
            print(f"  -" * 30)
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}\n错误处理测试报告\n{'='*60}")
        
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        helpful = sum(1 for r in self.results if r.response_helpful)
        avg_time = sum(r.response_time_ms for r in self.results) / total if total > 0 else 0
        
        print(f"\n总测试数: {total}")
        print(f"有响应: {success} ({success/total*100:.1f}%)")
        print(f"响应有帮助: {helpful} ({helpful/total*100:.1f}%)")
        print(f"平均响应时间: {avg_time:.0f}ms")
        
        # 按类别统计
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"total": 0, "helpful": 0}
            categories[r.category]["total"] += 1
            if r.response_helpful:
                categories[r.category]["helpful"] += 1
        
        print(f"\n按类别统计:")
        for cat, stats in categories.items():
            rate = stats["helpful"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {cat}: {stats['helpful']}/{stats['total']} 有帮助 ({rate:.1f}%)")
        
        # 成功标准检查
        print(f"\n成功标准检查:")
        criteria = {
            "90%+ 查询得到响应": success / total >= 0.9,
            "80%+ 响应有帮助": helpful / total >= 0.8,
            "响应时间 < 5秒": avg_time < 5000,
        }
        
        for criterion, passed in criteria.items():
            print(f"  {'✓' if passed else '✗'} {criterion}")
        
        # 保存报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "success": success,
                "helpful": helpful,
                "avg_time_ms": avg_time
            },
            "by_category": categories,
            "criteria": criteria,
            "results": [asdict(r) for r in self.results]
        }
        
        filename = f"error_handling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存: {filename}")
        
        return all(criteria.values())


def main():
    print("RAG 错误处理与智能提示 UI 自动化测试")
    print("REQ-02 使用 Playwright + Xvfb 虚拟显示")
    print("=" * 60)
    
    # 检查前端
    import requests
    try:
        resp = requests.get("http://localhost:3000", timeout=5)
        if resp.status_code != 200:
            print("⚠️  前端 UI 无法访问")
            return 1
    except:
        print("⚠️  前端 UI 无法访问")
        return 1
            
    # 使用非 headless 模式配合 Xvfb，可以获得更好的兼容性和截图
    tester = RAGErrorHandlingTester(headless=False, enable_screenshots=True)
    tester.run_tests()
    
    print("\n💡 提示: 所有截图已保存在 screenshots/ 目录")
    
    return 0


if __name__ == "__main__":
    exit(main())
