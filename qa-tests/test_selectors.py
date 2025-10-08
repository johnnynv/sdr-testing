#!/usr/bin/env python3
"""测试不同的选择器，找到正确的响应元素"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto("http://localhost:3000", timeout=60000)
    page.wait_for_load_state('domcontentloaded')
    time.sleep(2)
    
    # 提交查询
    query = "Summarize the last 10 minutes on channel 0"
    input_box = page.locator('textarea').first
    input_box.clear()
    time.sleep(0.3)
    input_box.type(query, delay=20)
    time.sleep(1)
    input_box.press('Enter')
    
    print("等待响应（20秒）...")
    time.sleep(20)
    
    print("\n" + "="*60)
    print("测试不同选择器")
    print("="*60)
    
    # 测试选择器
    selectors_to_test = [
        ('div.prose', 'div.prose'),
        ('prose dark:prose-invert', 'div[class*="prose dark:prose-invert"]'),
        ('prose whitespace-pre-wrap', 'div[class*="prose whitespace-pre-wrap"]'),
        ('whitespace-pre-wrap', 'div[class*="whitespace-pre-wrap"]'),
        ('group md:px-4', 'div[class*="group md:px-4"]'),
        ('border-b border-black', 'div[class*="border-b border-black"]'),
    ]
    
    for name, selector in selectors_to_test:
        try:
            elements = page.locator(selector).all()
            if len(elements) > 0:
                print(f"\n✓ {name}: 找到 {len(elements)} 个元素")
                # 获取每个元素的文本
                for i, elem in enumerate(elements):
                    try:
                        text = elem.inner_text()
                        if text and len(text) > 10:
                            print(f"  [{i}] {text[:80]}...")
                    except:
                        pass
        except Exception as e:
            print(f"✗ {name}: {e}")
    
    # 尝试获取所有聊天消息（用户+AI）
    print("\n" + "="*60)
    print("尝试获取完整对话")
    print("="*60)
    
    # 根据截图，对话似乎在group容器中
    chat_groups = page.locator('div[class*="group"]').all()
    print(f"找到 {len(chat_groups)} 个group容器")
    
    for i, group in enumerate(chat_groups):
        try:
            text = group.inner_text()
            if query[:20] in text or len(text) > 30:
                print(f"\nGroup {i}:")
                print(f"  {text[:150]}...")
        except:
            pass
    
    browser.close()

