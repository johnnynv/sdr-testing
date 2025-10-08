#!/usr/bin/env python3
"""
RAG UI 自动化测试统一启动器
整合了完整测试和快速测试功能
"""

import sys
import subprocess
import os
import requests
from pathlib import Path


def check_environment():
    """检查测试环境"""
    print("\n" + "=" * 60)
    print("环境检查")
    print("=" * 60)
    
    issues = []
    
    # 1. 检查 Xvfb
    result = subprocess.run(['which', 'xvfb-run'], capture_output=True)
    if result.returncode == 0:
        print("✓ Xvfb 已安装")
    else:
        print("✗ Xvfb 未安装")
        issues.append("请运行: sudo apt-get install xvfb")
    
    # 2. 检查虚拟环境
    if sys.prefix != sys.base_prefix:
        print("✓ 虚拟环境已激活")
    else:
        print("⚠️  虚拟环境未激活")
        issues.append("请运行: source venv/bin/activate")
    
    # 3. 检查前端服务
    try:
        resp = requests.get("http://localhost:3000", timeout=3)
        if resp.status_code == 200:
            print("✓ 前端服务运行正常 (http://localhost:3000)")
        else:
            print(f"⚠️  前端服务响应异常: {resp.status_code}")
            issues.append("检查前端服务状态")
    except:
        print("✗ 前端服务无法访问")
        issues.append("确保前端服务运行在 http://localhost:3000")
    
    # 4. 创建截图目录
    Path("screenshots").mkdir(exist_ok=True)
    print("✓ 截图目录已准备: ./screenshots/")
    
    if issues:
        print("\n❌ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True


def run_with_xvfb(script_name, *args):
    """使用 Xvfb 运行 Python 脚本"""
    cmd = [
        'xvfb-run',
        '-a',
        '--server-args=-screen 0 1920x1080x24',
        'python3',
        script_name
    ] + list(args)
    
    return subprocess.run(cmd)


def show_menu():
    """显示交互式菜单"""
    print("\n" + "=" * 60)
    print("RAG UI 自动化测试")
    print("=" * 60)
    print("  1. 时间过滤功能测试 (19 个测试用例)")
    print("  2. 错误处理测试 (19 个测试用例)")
    print("  3. 运行所有测试 (38 个测试用例)")
    print("  4. 快速测试单个查询")
    print("  0. 退出")
    print("=" * 60)
    
    try:
        choice = input("请选择 (0-4): ").strip()
        return choice
    except (KeyboardInterrupt, EOFError):
        print("\n\n已取消")
        return '0'


def run_time_filter_tests():
    """运行时间过滤功能测试"""
    print("\n🚀 运行时间过滤功能测试...")
    print("使用 Xvfb 虚拟显示 + 截图功能\n")
    result = run_with_xvfb('test_rag_time_filtering.py')
    return result.returncode


def run_error_handling_tests():
    """运行错误处理测试"""
    print("\n🚀 运行错误处理测试...")
    print("使用 Xvfb 虚拟显示 + 截图功能\n")
    result = run_with_xvfb('test_rag_error_handling.py')
    return result.returncode


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 运行所有测试...")
    print("使用 Xvfb 虚拟显示 + 截图功能\n")
    
    print("=" * 60)
    print("1/2: 时间过滤功能测试")
    print("=" * 60)
    result1 = run_with_xvfb('test_rag_time_filtering.py')
    
    print("\n\n" + "=" * 60)
    print("2/2: 错误处理测试")
    print("=" * 60)
    result2 = run_with_xvfb('test_rag_error_handling.py')
    
    return result1.returncode + result2.returncode


def quick_test():
    """快速测试单个查询"""
    print("\n" + "=" * 60)
    print("快速测试单个查询")
    print("=" * 60)
    
    # 获取查询
    try:
        query = input("请输入查询 (留空使用默认): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n已取消")
        return 0
    
    if not query:
        query = "Summarize the last 10 minutes on channel 0"
        print(f"使用默认查询: {query}")
    
    print(f"\n🚀 执行查询: {query}\n")
    result = run_with_xvfb('quick_test.py', query)
    return result.returncode


def show_results():
    """显示测试结果摘要"""
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    
    # 显示最新的报告
    import glob
    reports = sorted(glob.glob('*_report_*.json'), key=os.path.getmtime, reverse=True)
    
    if reports:
        print("\n📊 最新测试报告:")
        for report in reports[:5]:
            size = os.path.getsize(report)
            mtime = os.path.getmtime(report)
            from datetime import datetime
            time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {report:50} {size:>8} bytes  {time_str}")
    
    # 显示最新的截图
    screenshots = sorted(glob.glob('screenshots/*.png'), key=os.path.getmtime, reverse=True)
    if screenshots:
        print(f"\n📸 截图文件: {len(screenshots)} 张")
        print("   最新的 5 张:")
        for shot in screenshots[:5]:
            size = os.path.getsize(shot)
            mtime = os.path.getmtime(shot)
            time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {os.path.basename(shot):40} {size:>8} bytes  {time_str}")
    
    print("=" * 60)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("RAG UI 自动化测试启动器")
    print("Playwright + Xvfb")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复问题后重试")
        return 1
    
    # 交互式菜单
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_time_filter_tests()
            show_results()
        elif choice == '2':
            run_error_handling_tests()
            show_results()
        elif choice == '3':
            run_all_tests()
            show_results()
        elif choice == '4':
            quick_test()
        elif choice == '0':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选择，请重试")
        
        # 询问是否继续
        try:
            cont = input("\n按 Enter 继续，或输入 'q' 退出: ").strip().lower()
            if cont == 'q':
                print("\n👋 再见！")
                break
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 再见！")
            break
    
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
        exit(130)

