#!/usr/bin/env python3
"""使用通用方法找到消息（不依赖特定CSS类）"""

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
    
    # 等待响应
    print("等待响应...")
    for i in range(30):
        time.sleep(1)
        body_text = page.inner_text('body')
        if 'Thinking' not in body_text and 'Stop Generating' not in body_text:
            print(f"✓ 响应完成（{i+1}秒）")
            break
    
    time.sleep(2)
    
    # 方法1: 使用JavaScript找到包含查询和响应的所有文本块
    print("\n" + "="*60)
    print("方法1: JavaScript查找文本块")
    print("="*60)
    
    messages = page.evaluate(f'''() => {{
        const query = "{query}";
        const result = [];
        
        // 找到所有div, p, article元素
        const allElements = document.querySelectorAll('div, p, article, section');
        
        allElements.forEach((el, idx) => {{
            const text = el.innerText || '';
            
            // 如果元素包含查询文本或者是一个长度适中的文本块
            if ((text.includes(query) || text.length > 50) && text.length < 2000) {{
                // 排除包含大量子元素的容器
                const childDivs = el.querySelectorAll('div').length;
                if (childDivs < 5) {{
                    result.push({{
                        tag: el.tagName,
                        className: el.className,
                        text: text.substring(0, 200),
                        fullLength: text.length
                    }});
                }}
            }}
        }});
        
        return result;
    }}''')
    
    print(f"找到 {len(messages)} 个文本块:")
    for i, msg in enumerate(messages[-10:]):  # 显示最后10个
        print(f"\n[{i}] <{msg['tag']}> (共{msg['fullLength']}字符)")
        if msg['className']:
            print(f"    class: {msg['className'][:60]}...")
        print(f"    文本: {msg['text']}...")
    
    # 方法2: 简单提取所有prose元素（通常用于显示格式化文本）
    print("\n" + "="*60)
    print("方法2: 提取prose元素")
    print("="*60)
    
    prose_elements = page.locator('.prose').all()
    print(f"找到 {len(prose_elements)} 个prose元素")
    
    for i, elem in enumerate(prose_elements):
        try:
            text = elem.inner_text()
            if len(text) > 20:
                print(f"\n[{i}] ({len(text)} 字符): {text[:150]}...")
        except:
            pass
    
    # 方法3: 直接搜索包含查询文本和不包含查询文本的div（用于区分用户消息和AI响应）
    print("\n" + "="*60)
    print("方法3: 区分用户消息和AI响应")
    print("="*60)
    
    # 找到包含查询的元素（用户消息）
    user_message = page.locator(f'text="{query}"').first
    if user_message.count() > 0:
        print(f"✓ 找到用户消息")
    
    # 获取整个body的文本，然后分析
    full_body_text = page.inner_text('body')
    
    # 尝试找到查询之后的文本（应该是响应）
    query_pos = full_body_text.find(query)
    if query_pos >= 0:
        after_query = full_body_text[query_pos + len(query):query_pos + len(query) + 500]
        print(f"\n查询之后的文本（500字符）:")
        print(f"{after_query}")
    
    browser.close()

