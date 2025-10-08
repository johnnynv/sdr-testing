#!/usr/bin/env python3
"""
快速测试单个查询 - 使用 Xvfb + Playwright
适合调试和快速验证单个查询
"""

import sys
from playwright.sync_api import sync_playwright
from datetime import datetime


def quick_test(query: str):
    """快速测试单个查询并截图"""
    print(f"\n🚀 快速测试")
    print(f"查询: {query}")
    print("=" * 60)
    
    with sync_playwright() as p:
        # 启动浏览器（非 headless 模式配合 Xvfb）
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 访问前端
            print("📱 访问前端 UI...")
            page.goto("http://localhost:3000", timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            
            # 输入查询
            print("⌨️  输入查询...")
            input_box = page.locator('textarea, input[type="text"]').first
            input_box.clear()
            page.wait_for_timeout(300)
            
            # 使用 type 方法逐字符输入
            input_box.type(query, delay=20)
            page.wait_for_timeout(1000)
            
            # 验证输入
            current_value = input_box.input_value()
            print(f"✓ 已输入 {len(current_value)} 字符")
            
            # 确保输入框聚焦
            input_box.focus()
            page.wait_for_timeout(500)
            
            # 截图：输入后提交前
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"screenshots/quick_input_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 输入截图: {screenshot_path}")
            
            # 提交
            print("📤 提交查询...")
            input_box.press('Enter')
            
            # 等待响应 - 使用更长的超时时间
            print("⏳ 等待响应（最多 30 秒）...")
            try:
                # 等待页面内容变化或新元素出现
                page.wait_for_timeout(10000)  # 先等10秒让系统处理
            except:
                pass
            
            # 截图：响应后
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"screenshots/quick_response_{timestamp}.png"
            import os
            os.makedirs("screenshots", exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            
            # 尝试多种方式获取响应
            print("\n🔍 查找响应...")
            
            # 方法1: 查找所有文本内容
            all_text = page.inner_text('body')
            
            # 方法2: 尝试不同的选择器
            selectors = [
                '[class*="message"]',
                '[class*="chat"]',
                '[class*="response"]',
                'div[class*="bg-white dark:bg-gray-700"]',  # 从HTML看到的stream显示区域
                'p[class*="text-black dark:text-white"]'
            ]
            
            found_response = False
            for selector in selectors:
                elements = page.locator(selector).all()
                if elements:
                    print(f"  ✓ 找到 {len(elements)} 个元素: {selector}")
                    for elem in elements[-3:]:  # 显示最后3个
                        try:
                            text = elem.inner_text().strip()
                            if text and len(text) > 10 and query[:20] not in text:  # 排除输入框本身
                                print(f"\n✅ 收到响应:")
                                print("-" * 60)
                                print(text[:500])
                                if len(text) > 500:
                                    print("...")
                                print("-" * 60)
                                found_response = True
                                break
                        except:
                            pass
                if found_response:
                    break
            
            if not found_response:
                print("\n⚠️  未检测到新响应")
                print("页面主要内容:")
                print(all_text[:500] if len(all_text) > 0 else "  (页面为空)")
            
            print(f"\n📸 截图已保存: {screenshot_path}")
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            
        finally:
            browser.close()
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数获取查询
        query = " ".join(sys.argv[1:])
    else:
        # 默认查询
        query = "Summarize the last 10 minutes on channel 0"
        print(f"💡 提示: 使用方式: python3 quick_test.py \"your query here\"")
        print(f"   使用默认查询: {query}\n")
    
    quick_test(query)

