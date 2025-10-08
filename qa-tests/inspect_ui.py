#!/usr/bin/env python3
"""检查UI结构，找到正确的选择器"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("访问页面...")
    page.goto("http://localhost:3000", timeout=60000)
    page.wait_for_load_state('domcontentloaded')
    time.sleep(2)
    
    # 输入并提交查询
    query = "Summarize the last 10 minutes on channel 0"
    print(f"输入查询: {query}")
    
    input_box = page.locator('textarea').first
    input_box.clear()
    time.sleep(0.5)
    input_box.type(query, delay=30)
    time.sleep(1)
    
    page.screenshot(path="screenshots/inspect_before_submit.png", full_page=True)
    print("✓ 截图：提交前")
    
    input_box.press('Enter')
    print("已提交，等待响应...")
    time.sleep(15)
    
    page.screenshot(path="screenshots/inspect_after_response.png", full_page=True)
    print("✓ 截图：响应后")
    
    # 尝试找到聊天消息容器
    print("\n" + "="*60)
    print("查找聊天消息")
    print("="*60)
    
    # 获取页面的主要结构
    print("\n查找主容器元素:")
    main_selectors = [
        'main',
        'div[role="main"]',
        'div[class*="chat"]',
        'div[class*="conversation"]',
        'div[class*="messages"]',
    ]
    
    for selector in main_selectors:
        count = page.locator(selector).count()
        if count > 0:
            print(f"  ✓ {selector}: {count} 个")
    
    # 查找所有可能包含消息的div
    print("\n查找所有div，分析结构:")
    all_divs = page.locator('div').all()
    print(f"  总共 {len(all_divs)} 个div元素")
    
    # 查找包含用户图标或机器人图标的元素
    print("\n查找图标元素:")
    icon_selectors = [
        'svg',
        '[class*="icon"]',
        '[class*="avatar"]',
        'img',
    ]
    
    for selector in icon_selectors:
        count = page.locator(selector).count()
        if count > 0:
            print(f"  ✓ {selector}: {count} 个")
    
    # 使用 evaluate 获取更详细的DOM结构
    print("\n" + "="*60)
    print("分析DOM结构（JavaScript）")
    print("="*60)
    
    structure = page.evaluate('''() => {
        // 查找所有文本节点，找出可能是消息的部分
        const messages = [];
        const allElements = document.querySelectorAll('div, p, span');
        
        allElements.forEach((el, idx) => {
            const text = el.innerText;
            if (text && text.length > 20 && text.length < 500) {
                // 可能是消息内容
                const className = el.className || '';
                const tagName = el.tagName;
                messages.push({
                    index: idx,
                    tag: tagName,
                    class: className,
                    text: text.substring(0, 100)
                });
            }
        });
        
        return {
            messageCount: messages.length,
            messages: messages.slice(-10)  // 最后10个
        };
    }''')
    
    print(f"\n找到 {structure['messageCount']} 个可能的消息元素")
    print("\n最后10个元素:")
    for msg in structure['messages']:
        print(f"\n  [{msg['index']}] <{msg['tag']}> class='{msg['class'][:50]}...'")
        print(f"      文本: {msg['text']}...")
    
    # 保存完整HTML
    html = page.content()
    with open("screenshots/page_full.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✓ 完整HTML已保存: screenshots/page_full.html")
    
    browser.close()
    
print("\n分析完成！请查看:")
print("  1. screenshots/inspect_before_submit.png")
print("  2. screenshots/inspect_after_response.png")
print("  3. screenshots/page_full.html")
