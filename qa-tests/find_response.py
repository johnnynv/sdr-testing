#!/usr/bin/env python3
"""找到AI响应的正确方法"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto("http://localhost:3000", timeout=60000)
    page.wait_for_load_state('domcontentloaded')
    time.sleep(2)
    
    query = "Summarize the last 10 minutes on channel 0"
    input_box = page.locator('textarea').first
    input_box.clear()
    time.sleep(0.3)
    input_box.type(query, delay=20)
    time.sleep(1)
    
    print(f"提交查询: {query}")
    input_box.press('Enter')
    
    # 等待"Thinking"消失，说明响应开始生成
    print("等待AI响应...")
    for i in range(40):  # 最多等待40秒
        time.sleep(1)
        body_text = page.inner_text('body')
        if 'Thinking' not in body_text:
            print(f"✓ 响应开始生成（{i+1}秒后）")
            break
        if i % 5 == 0:
            print(f"  ...等待中 ({i}秒)")
    
    # 再等待5秒让响应完全显示
    time.sleep(5)
    
    # 截图
    page.screenshot(path="screenshots/response_完整.png", full_page=True)
    print("✓ 截图已保存")
    
    # 尝试不同方法获取响应
    print("\n" + "="*60)
    print("方法1: 查找所有group容器（通常每个消息一个）")
    print("="*60)
    
    groups = page.locator('div[class*="group"][class*="border-b"]').all()
    print(f"找到 {len(groups)} 个消息组")
    
    for i, group in enumerate(groups):
        text = group.inner_text()
        print(f"\n消息 {i+1}:")
        print(f"  {text[:200]}...")
    
    # 方法2: 查找所有prose元素
    print("\n" + "="*60)
    print("方法2: 查找所有prose内容元素")
    print("="*60)
    
    prose_elements = page.locator('div.prose').all()
    print(f"找到 {len(prose_elements)} 个prose元素")
    
    for i, elem in enumerate(prose_elements):
        text = elem.inner_text()
        if len(text) > 10:
            print(f"\nProse {i+1}:")
            print(f"  {text[:200]}...")
    
    # 方法3: 使用JavaScript获取对话历史
    print("\n" + "="*60)
    print("方法3: JavaScript提取对话")
    print("="*60)
    
    messages = page.evaluate('''() => {
        const result = [];
        
        // 查找所有包含消息的容器
        // 通常用户消息和AI响应在不同的div中
        const messageContainers = document.querySelectorAll('div[class*="group"][class*="border"]');
        
        messageContainers.forEach((container, idx) => {
            // 获取文本内容
            const text = container.innerText || '';
            
            // 检查是否包含我们的查询或响应
            if (text.length > 20) {
                result.push({
                    index: idx,
                    preview: text.substring(0, 300),
                    length: text.length
                });
            }
        });
        
        return result;
    }''')
    
    print(f"找到 {len(messages)} 条消息:")
    for msg in messages:
        print(f"\n消息 {msg['index']+1} ({msg['length']} 字符):")
        print(f"  {msg['preview']}...")
    
    browser.close()

