#!/usr/bin/env python3
"""
RAG 系统时间过滤功能 UI 自动化测试
使用 Playwright 进行端到端测试
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
import pytz
from playwright.sync_api import sync_playwright, Page, expect


@dataclass
class TestResult:
    test_id: str
    test_name: str
    query: str
    success: bool
    has_response: bool
    response_time_ms: float
    error_message: Optional[str] = None


class RAGTimeFilterTester:
    def __init__(self, ui_url: str = "http://localhost:3000", headless: bool = False, enable_screenshots: bool = True):
        self.ui_url = ui_url
        self.headless = headless
        self.enable_screenshots = enable_screenshots
        self.results: List[TestResult] = []
        self.test_start_time = datetime.now(pytz.UTC)
    
    def execute_query(self, page: Page, query: str, timeout: int = 30000, screenshot: bool = True) -> TestResult:
        """执行查询并返回结果"""
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
                screenshot_path = f"screenshots/input_{timestamp}.png"
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
            
            # 等待"Thinking"消失，说明响应开始生成
            print(f"    ⏳ 等待AI响应（最多40秒）...")
            response_started = False
            for i in range(40):
                page.wait_for_timeout(1000)
                body_text = page.inner_text('body')
                if 'Thinking' not in body_text and 'Stop Generating' not in body_text:
                    print(f"    ✓ 响应已生成（{i+1}秒）")
                    response_started = True
                    break
                if i % 5 == 4:  # 每5秒报告一次
                    print(f"       ...处理中 ({i+1}秒)")
            
            if not response_started:
                print(f"    ⚠️  响应超时")
            
            # 再等待3秒确保渲染完成
            page.wait_for_timeout(3000)
            print(f"    ✓ DOM渲染完成")
            
            # 截图2: 响应后
            if screenshot and self.enable_screenshots:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"screenshots/response_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    📸 截图（响应后）: {screenshot_path}")
                
                import os
                size = os.path.getsize(screenshot_path)
                print(f"       文件大小: {size/1024:.1f} KB")
            
            # 检查响应 - 使用JavaScript方法提取（最可靠）
            print(f"    ⏳ 提取响应内容...")
            
            # 使用JavaScript获取body文本（比Playwright的inner_text更可靠）
            full_body_text = page.evaluate('() => document.body.innerText')
            
            # 调试：显示body文本长度
            print(f"       Body文本长度: {len(full_body_text)} 字符")
            query_pos = full_body_text.find(query)
            print(f"       查询位置: {query_pos if query_pos >= 0 else '未找到'}")
            
            has_response = False
            ai_response = ""
            
            if query_pos >= 0:
                # 提取查询之后的文本，直到遇到"Regenerate response"或达到最大长度
                after_query = full_body_text[query_pos + len(query):]
                
                # 清理文本：去除前后空白和换行
                after_query = after_query.strip()
                
                # 查找响应结束标记
                end_markers = ['Regenerate response', 'Stop Generating', '\n\n\n']
                end_pos = len(after_query)
                for marker in end_markers:
                    marker_pos = after_query.find(marker)
                    if marker_pos > 0 and marker_pos < end_pos:
                        end_pos = marker_pos
                
                ai_response = after_query[:end_pos].strip()
                
                # 验证响应不为空且不等于查询本身
                if ai_response and ai_response != query and len(ai_response) > 10:
                    has_response = True
                    print(f"    ✓ AI响应（{len(ai_response)} 字符）: {ai_response[:100]}...")
                else:
                    print(f"    ⚠️  响应为空或无效")
            else:
                print(f"    ⚠️  未在页面中找到查询文本")
            
            elapsed = (time.time() - start_time) * 1000
            
            return TestResult(
                test_id="",
                test_name="",
                query=query,
                success=has_response,
                has_response=has_response,
                response_time_ms=elapsed
            )
            
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
            elapsed = (time.time() - start_time) * 1000
            return TestResult(
                test_id="",
                test_name="",
                query=query,
                success=False,
                has_response=False,
                response_time_ms=elapsed,
                error_message=str(e)
            )
    
    def run_tests(self):
        """执行所有测试"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(self.ui_url, timeout=60000)  # 60秒超时
            page.wait_for_load_state('domcontentloaded')  # 等待 DOM 加载即可，不等待所有网络请求
            
            print(f"\n{'='*60}\n访问前端: {self.ui_url}\n测试开始时间: {self.test_start_time.isoformat()}\n{'='*60}")
            
            # 执行测试套件
            self.test_recent_summary(page)
            self.test_time_windows(page)
            self.test_excluding_recent(page)
            self.test_boundary_conditions(page)
            self.test_error_handling(page)
            
            browser.close()
        
        # 生成报告
        self.generate_report()
    
    def test_recent_summary(self, page: Page):
        """测试相对时间查询"""
        print(f"\n{'='*60}\n测试 1: 相对时间查询（Recent Summary）\n{'='*60}")
        
        tests = [
            ("TC_1.1", "最近10分钟 - Channel 0", "Summarize the last 10 minutes on channel 0"),
            ("TC_1.2", "最近5分钟 - Channel 1", "What was discussed in the last 5 minutes on channel 1?"),
            ("TC_1.3", "最近30分钟 - 所有通道", "Summarize the last 30 minutes across all channels"),
            ("TC_1.4", "最近1小时", "Summarize the main topics discussed for the past hour"),
            ("TC_1.5", "排除 Channel 2", "Summarize the main topics discussed, excluding channel 2, for the past hour"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            result = self.execute_query(page, query)
            result.test_id = test_id
            result.test_name = name
            self.results.append(result)
            status = "✓ 成功" if result.success else "✗ 失败"
            print(f"  结果: {status} | 响应时间: {result.response_time_ms:.0f}ms")
            print(f"  -" * 30)
    
    def test_time_windows(self, page: Page):
        """测试时间窗口查询"""
        print(f"\n{'='*60}\n测试 2: 时间窗口查询\n{'='*60}")
        
        tests = [
            ("TC_2.1", "15分钟前 - Channel 2", "What was the topic of conversation on channel 2 15 minutes ago?"),
            ("TC_2.2", "2-30分钟前", "Between 2 minutes and half an hour ago, what was the most interesting fact you heard?"),
            ("TC_2.3", "5-20分钟前 - Channel 1", "Between 5 and 20 minutes ago on channel 1, what topics were discussed?"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            result = self.execute_query(page, query)
            result.test_id = test_id
            result.test_name = name
            self.results.append(result)
            print(f"  结果: {'✓ 成功' if result.success else '✗ 失败'} | {result.response_time_ms:.0f}ms")
            print(f"  -" * 30)
    
    def test_excluding_recent(self, page: Page):
        """测试排除最近内容"""
        print(f"\n{'='*60}\n测试 3: 排除最近内容\n{'='*60}")
        
        tests = [
            ("TC_3.1", "排除最近10分钟", "What was the main topic of conversation on channel 0, excluding the past ten minutes?"),
            ("TC_3.2", "排除最近5分钟", "Summarize the topics on channel 2, excluding the last 5 minutes"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            result = self.execute_query(page, query)
            result.test_id = test_id
            result.test_name = name
            self.results.append(result)
            print(f"  结果: {'✓ 成功' if result.success else '✗ 失败'} | {result.response_time_ms:.0f}ms")
            print(f"  -" * 30)
    
    def test_boundary_conditions(self, page: Page):
        """测试边界条件"""
        print(f"\n{'='*60}\n测试 4: 边界条件\n{'='*60}")
        
        tests = [
            ("TC_4.1", "精确时间窗口", "What was discussed between exactly 10 minutes and 9 minutes ago on channel 0?"),
            ("TC_4.2", "未来时间（应无结果）", "What will be discussed 10 minutes from now on channel 0?"),
            ("TC_4.3", "很久以前（应无/少结果）", "What was discussed 10 hours ago on channel 2?"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            result = self.execute_query(page, query)
            result.test_id = test_id
            result.test_name = name
            self.results.append(result)
            print(f"  结果: {'✓ 执行' if result.success else '✗ 失败'} | {result.response_time_ms:.0f}ms")
            print(f"  -" * 30)
    
    def test_error_handling(self, page: Page):
        """测试错误处理"""
        print(f"\n{'='*60}\n测试 5: 错误处理\n{'='*60}")
        
        tests = [
            ("TC_5.1", "无效小时格式", "What was discussed at 25:00 on channel 0?"),
            ("TC_5.2", "负时间范围", "Summarize the last -10 minutes"),
            ("TC_5.3", "无效通道", "Summarize channel 999 from the last hour"),
            ("TC_5.4", "倒序时间", "What was discussed between 30 minutes ago and 1 hour ago?"),
        ]
        
        for idx, (test_id, name, query) in enumerate(tests, 1):
            print(f"\n▶ 测试 {idx}/{len(tests)}: {name}")
            print(f"  查询: {query}")
            result = self.execute_query(page, query)
            result.test_id = test_id
            result.test_name = name
            self.results.append(result)
            print(f"  结果: {'✓ 处理' if result.success else '✗ 失败'} | {result.response_time_ms:.0f}ms")
            print(f"  -" * 30)
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}\n测试报告\n{'='*60}")
        
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        avg_time = sum(r.response_time_ms for r in self.results) / total if total > 0 else 0
        
        print(f"\n测试时间: {self.test_start_time.isoformat()}")
        print(f"总测试数: {total}")
        print(f"成功: {success} ({success/total*100:.1f}%)")
        print(f"失败: {total-success} ({(total-success)/total*100:.1f}%)")
        print(f"平均响应时间: {avg_time:.0f}ms")
        
        # 失败的测试
        failed = [r for r in self.results if not r.success]
        if failed:
            print(f"\n失败的测试:")
            for r in failed:
                print(f"  - {r.test_id}: {r.test_name}")
                if r.error_message:
                    print(f"    错误: {r.error_message[:100]}")
        else:
            print(f"\n✓ 所有测试通过！")
        
        # 保存报告
        report = {
            "timestamp": self.test_start_time.isoformat(),
            "total": total,
            "success": success,
            "failed": total - success,
            "avg_response_time_ms": avg_time,
            "results": [asdict(r) for r in self.results]
        }
        
        filename = f"time_filter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存: {filename}")
        
        return success >= total * 0.8  # 80% 通过率


def main():
    print("RAG 时间过滤功能 UI 自动化测试")
    print("使用 Playwright + Xvfb 虚拟显示")
    print("=" * 60)
    
    # 检查前端是否可访问
    import requests
    try:
        resp = requests.get("http://localhost:3000", timeout=5)
        if resp.status_code != 200:
            print("⚠️  前端 UI 无法访问，请确保服务运行在 http://localhost:3000")
            return 1
    except:
        print("⚠️  前端 UI 无法访问，请确保服务运行在 http://localhost:3000")
        return 1
            
    # 使用非 headless 模式配合 Xvfb，可以获得更好的兼容性和截图
    tester = RAGTimeFilterTester(headless=False, enable_screenshots=True)
    tester.run_tests()
    
    print("\n💡 提示: 所有截图已保存在 screenshots/ 目录")
    
    return 0


if __name__ == "__main__":
    exit(main())
