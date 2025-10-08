#!/usr/bin/env python3
"""调试文本提取问题"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto("http://localhost:3000", timeout=60000)
    page.wait_for_load_state('domcontentloaded')
    time.sleep(2)
    
    query = "Summarize the last 10 minutes on channel 0"
    
    # 不刷新页面，直接输入
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
    
    # 提取body文本
    full_body_text = page.inner_text('body')
    
    print("\n" + "="*60)
    print("分析body文本")
    print("="*60)
    print(f"总长度: {len(full_body_text)} 字符")
    print(f"\n前1000字符:")
    print(full_body_text[:1000])
    print("\n" + "="*60)
    
    # 检查查询是否在其中
    if query in full_body_text:
        print(f"✓ 找到查询文本")
        query_pos = full_body_text.find(query)
        print(f"  位置: {query_pos}")
        print(f"  查询前50字符: ...{full_body_text[max(0,query_pos-50):query_pos]}")
        print(f"  查询: {full_body_text[query_pos:query_pos+len(query)]}")
        print(f"  查询后200字符: {full_body_text[query_pos+len(query):query_pos+len(query)+200]}...")
    else:
        print(f"✗ 未找到查询文本")
        print(f"  尝试查找部分文本...")
        if "Summarize" in full_body_text:
            print(f"  ✓ 找到 'Summarize'")
        if "channel 0" in full_body_text:
            print(f"  ✓ 找到 'channel 0'")
        if "last 10 minutes" in full_body_text:
            print(f"  ✓ 找到 'last 10 minutes'")
    
    browser.close()
