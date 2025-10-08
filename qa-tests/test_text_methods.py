#!/usr/bin/env python3
"""测试不同的文本提取方法"""

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
    
    print(f"提交查询...")
    input_box.press('Enter')
    
    # 等待响应
    for i in range(30):
        time.sleep(1)
        body_text = page.inner_text('body')
        if 'Thinking' not in body_text and 'Stop Generating' not in body_text:
            print(f"✓ 响应完成（{i+1}秒）")
            break
    
    time.sleep(3)
    
    print("\n" + "="*60)
    print("测试不同的文本提取方法")
    print("="*60)
    
    # 方法1: inner_text
    text1 = page.inner_text('body')
    print(f"\n1. inner_text('body'): {len(text1)} 字符")
    print(f"   包含查询? {query in text1}")
    if query not in text1:
        print(f"   前200字符: {text1[:200]}...")
    
    # 方法2: text_content  
    text2 = page.locator('body').text_content()
    print(f"\n2. textContent: {len(text2) if text2 else 0} 字符")
    if text2:
        print(f"   包含查询? {query in text2}")
    
    # 方法3: JavaScript innerText
    text3 = page.evaluate('() => document.body.innerText')
    print(f"\n3. JS innerText: {len(text3)} 字符")
    print(f"   包含查询? {query in text3}")
    if query in text3:
        pos = text3.find(query)
        print(f"   查询位置: {pos}")
        print(f"   查询后200字符: {text3[pos+len(query):pos+len(query)+200]}")
    else:
        print(f"   前200字符: {text3[:200]}...")
    
    # 方法4: 查找prose元素
    prose_elements = page.locator('.prose, [class*="prose"]').all()
    print(f"\n4. Prose元素: {len(prose_elements)} 个")
    all_prose_text = []
    for i, elem in enumerate(prose_elements):
        try:
            text = elem.inner_text()
            all_prose_text.append(text)
            print(f"   [{i}] ({len(text)} 字符): {text[:80]}...")
        except:
            pass
    
    combined_prose = "\\n".join(all_prose_text)
    print(f"\n   合并后: {len(combined_prose)} 字符")
    print(f"   包含查询? {query in combined_prose}")
    if query in combined_prose:
        pos = combined_prose.find(query)
        print(f"   查询后200字符: {combined_prose[pos+len(query):pos+len(query)+200]}")
    
    browser.close()

