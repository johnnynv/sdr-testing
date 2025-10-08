#!/usr/bin/env python3
"""检查选择器是否正确"""

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
    
    print("提交查询...")
    input_box.press('Enter')
    
    # 等待响应
    print("等待响应...")
    for i in range(30):
        time.sleep(1)
        body_text = page.inner_text('body')
        if 'Thinking' not in body_text and 'Stop Generating' not in body_text:
            print(f"响应完成（{i+1}秒）")
            break
    
    time.sleep(3)
    
    # 测试不同选择器
    print("\n" + "="*60)
    print("测试所有可能的选择器")
    print("="*60)
    
    selectors = [
        ('div[class*="group"]', 'group类'),
        ('div[class*="border-b"]', 'border-b类'),
        ('div[class*="group"][class*="border-b"]', 'group+border-b'),
        ('div[class*="group"][class*="border"]', 'group+border'),
        ('div.group', '精确.group'),
        ('div[class*="md:px-4"]', 'md:px-4'),
        ('.prose', '.prose类'),
        ('div.prose', 'div.prose'),
    ]
    
    for name, selector in selectors:
        count = page.locator(selector).count()
        print(f"\n{name:25} ({selector})")
        print(f"  找到: {count} 个元素")
        
        if count > 0 and count <= 5:
            elements = page.locator(selector).all()
            for i, elem in enumerate(elements):
                try:
                    text = elem.inner_text()[:80]
                    print(f"    [{i}] {text}...")
                except:
                    print(f"    [{i}] (无法读取)")
    
    # 使用JavaScript检查DOM
    print("\n" + "="*60)
    print("JavaScript DOM检查")
    print("="*60)
    
    dom_info = page.evaluate('''() => {
        const info = {};
        
        // 检查所有包含"group"的类
        const groupElements = document.querySelectorAll('[class*="group"]');
        info.groupCount = groupElements.length;
        info.groupClasses = [];
        groupElements.forEach((el, i) => {
            if (i < 5) {
                info.groupClasses.push(el.className);
            }
        });
        
        // 检查所有包含"border"的类
        const borderElements = document.querySelectorAll('[class*="border"]');
        info.borderCount = borderElements.length;
        
        // 检查prose元素
        const proseElements = document.querySelectorAll('.prose, [class*="prose"]');
        info.proseCount = proseElements.length;
        
        return info;
    }''')
    
    print(f"\ngroup元素: {dom_info['groupCount']} 个")
    print("前5个的class:")
    for cls in dom_info['groupClasses']:
        print(f"  {cls[:100]}...")
    
    print(f"\nborder元素: {dom_info['borderCount']} 个")
    print(f"prose元素: {dom_info['proseCount']} 个")
    
    # 保存截图和HTML
    page.screenshot(path="screenshots/selector_check.png", full_page=True)
    with open("screenshots/selector_check.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    print("\n✓ 已保存: screenshots/selector_check.png 和 selector_check.html")
    
    browser.close()
