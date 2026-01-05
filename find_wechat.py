"""
查找微信安装路径工具
帮助用户找到微信程序的位置
"""

import os
import sys
import json
from pathlib import Path


def find_from_config():
    """从配置文件读取微信路径"""
    print("\n[1] 从配置文件查找...")
    
    config_file = Path("config/config.json")
    
    if not config_file.exists():
        print("  ⚠️ 配置文件不存在")
        return []
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        wechat_path = config.get('wechat_path', '')
        
        if wechat_path and os.path.exists(wechat_path):
            print(f"  ✅ 找到: {wechat_path}")
            return [wechat_path]
        elif wechat_path:
            print(f"  ⚠️ 配置的路径不存在: {wechat_path}")
        else:
            print("  ⚠️ 配置文件中未设置微信路径")
        
        return []
    except Exception as e:
        print(f"  ⚠️ 读取配置失败: {e}")
        return []


def find_from_common_paths():
    """从常见路径查找微信"""
    print("\n[2] 从常见安装路径查找...")
    
    common_paths = [
        os.path.expandvars(r"%ProgramFiles%\Tencent\WeChat\WeChat.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Tencent\WeChat\WeChat.exe"),
        os.path.expandvars(r"%LocalAppData%\Tencent\WeChat\WeChat.exe"),
        os.path.expandvars(r"%AppData%\Tencent\WeChat\WeChat.exe"),
        r"C:\Program Files\Tencent\WeChat\WeChat.exe",
        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
    ]
    
    found_paths = []
    for wechat_path in common_paths:
        if os.path.exists(wechat_path):
            found_paths.append(wechat_path)
            print(f"  ✅ 找到: {wechat_path}")
    
    if not found_paths:
        print("  ⚠️ 未在常见路径找到微信")
    
    return found_paths


def save_to_config(wechat_path):
    """保存微信路径到配置文件"""
    config_file = Path("config/config.json")
    
    try:
        # 读取现有配置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 更新配置
        config['wechat_path'] = wechat_path
        config['wechat_enabled'] = True
        
        # 保存配置
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 配置已保存到: {config_file}")
        return True
    except Exception as e:
        print(f"\n❌ 保存配置失败: {e}")
        return False


def main():
    print("=" * 60)
    print("微信路径查找工具")
    print("=" * 60)
    
    # 收集所有找到的路径
    all_paths = []
    
    # 方法 1: 配置文件
    paths = find_from_config()
    all_paths.extend(paths)
    
    # 方法 2: 常见路径
    paths = find_from_common_paths()
    all_paths.extend(paths)
    
    # 去重
    all_paths = list(dict.fromkeys(all_paths))  # 保持顺序的去重
    
    # 显示结果
    print("\n" + "=" * 60)
    print("查找结果")
    print("=" * 60)
    
    if not all_paths:
        print("\n❌ 未找到微信安装路径")
        print("\n可能的原因：")
        print("  1. 微信未安装")
        print("  2. 微信安装在非标准位置")
        print("\n解决方案：")
        print("  1. 从官网下载安装微信：https://weixin.qq.com/")
        print("  2. 手动查找 WeChat.exe 位置")
        print("  3. 手动编辑 config/config.json，添加：")
        print('     "wechat_path": "完整路径\\WeChat.exe"')
        return 1
    
    print(f"\n找到 {len(all_paths)} 个微信安装：")
    for i, path in enumerate(all_paths, 1):
        print(f"  [{i}] {path}")
    
    # 询问用户选择
    if len(all_paths) == 1:
        print(f"\n使用找到的路径: {all_paths[0]}")
        selected_path = all_paths[0]
    else:
        try:
            print("\n请选择要使用的路径（输入序号）:")
            choice = int(input(f"选择 [1-{len(all_paths)}]: "))
            if 1 <= choice <= len(all_paths):
                selected_path = all_paths[choice - 1]
            else:
                print("❌ 无效的选择")
                return 1
        except (ValueError, KeyboardInterrupt):
            print("\n❌ 已取消")
            return 1
    
    # 保存到配置
    print(f"\n选择的路径: {selected_path}")
    if save_to_config(selected_path):
        print("\n✅ 完成！现在可以在应用中使用微信功能了")
        print("\n下一步:")
        print("  1. 启动应用: python src/main.py")
        print("  2. 配置微信报警")
        print("  3. 开始监控")
        return 0
    else:
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
