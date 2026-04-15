#!/usr/bin/env python3
"""
YidaSkillHub 辅助脚本
用于下载和管理技能
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# 默认配置
DEFAULT_CONFIG = {
    "vault": {
        "url": "github:logda/YidaSkillHub",
        "branch": "main"
    },
    "settings": {
        "default_install_location": "ask",
        "auto_update_check": True
    }
}

CONFIG_DIR = Path.home() / ".YidaSkillHub"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def parse_github_url(url: str) -> Tuple[str, str]:
    """解析 github:owner/repo 格式"""
    if url.startswith("github:"):
        url = url[7:]
    parts = url.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    raise ValueError(f"Invalid GitHub URL format: {url}")


def get_manifest(owner: str, repo: str, branch: str = "main") -> Optional[Dict]:
    """从GitHub下载manifest.json"""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/manifest.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching manifest: {e}", file=sys.stderr)
        return None


def get_repo_tree(owner: str, repo: str, branch: str = "main") -> Optional[List[Dict]]:
    """获取仓库文件树"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'YidaSkillHub')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('tree', [])
    except Exception as e:
        print(f"Error fetching repo tree: {e}", file=sys.stderr)
        return None


def download_file(owner: str, repo: str, path: str, branch: str = "main") -> Optional[bytes]:
    """下载单个文件"""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except Exception as e:
        print(f"Error downloading {path}: {e}", file=sys.stderr)
        return None


def init_config():
    """初始化配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if not CONFIG_FILE.exists():
        # 写入YAML格式的默认配置
        config_content = """# YidaSkillHub 配置文件

vault:
  url: "github:logda/YidaSkillHub"  # GitHub仓库地址
  branch: "main"                    # 分支名

settings:
  default_install_location: "ask"   # ask | global | local
  auto_update_check: true
"""
        CONFIG_FILE.write_text(config_content)
        print(f"✅ 配置文件已创建: {CONFIG_FILE}")
    else:
        print(f"ℹ️ 配置文件已存在: {CONFIG_FILE}")
    
    # 创建本地技能存储目录
    local_skills = CONFIG_DIR / "local-skills"
    local_skills.mkdir(exist_ok=True)
    
    return True


def list_available_skills(owner: str, repo: str, branch: str = "main"):
    """列出所有可用技能"""
    manifest = get_manifest(owner, repo, branch)
    if not manifest:
        print("❌ 无法获取技能清单", file=sys.stderr)
        return False
    
    skills = manifest.get('skills', {})
    if not skills:
        print("📭 暂无可用技能")
        return True
    
    print(f"\n📦 YidaSkillHub 可用技能 (共 {len(skills)} 个):\n")
    
    for i, (name, info) in enumerate(skills.items(), 1):
        version = info.get('version', 'unknown')
        description = info.get('description', '无描述')
        tags = info.get('tags', [])
        
        print(f"{i}. {name} (v{version})")
        print(f"   {description}")
        if tags:
            print(f"   标签: {', '.join(tags)}")
        print()
    
    return True


def install_skill(skill_name: str, location: str, owner: str, repo: str, branch: str = "main"):
    """安装技能"""
    # 确定安装路径
    if location == "global":
        install_dir = Path.home() / ".agents" / "skills" / skill_name
    else:  # local
        install_dir = Path(".agents") / "skills" / skill_name
    
    # 检查是否已存在
    if install_dir.exists():
        print(f"⚠️ 技能 {skill_name} 已存在于 {install_dir}")
        return False
    
    # 获取manifest确认技能存在
    manifest = get_manifest(owner, repo, branch)
    if not manifest or skill_name not in manifest.get('skills', {}):
        print(f"❌ 技能 {skill_name} 不存在于仓库中")
        return False
    
    skill_info = manifest['skills'][skill_name]
    skill_path = skill_info.get('path', f"skills/{skill_name}")
    
    print(f"📥 正在下载 {skill_name} v{skill_info.get('version', 'unknown')}...")
    
    # 获取文件树
    tree = get_repo_tree(owner, repo, branch)
    if not tree:
        print("❌ 无法获取仓库文件树", file=sys.stderr)
        return False
    
    # 筛选技能相关文件
    skill_files = [
        item for item in tree
        if item['path'].startswith(skill_path) and item['type'] == 'blob'
    ]
    
    if not skill_files:
        print(f"❌ 未找到技能文件: {skill_path}")
        return False
    
    # 下载所有文件
    install_dir.mkdir(parents=True, exist_ok=True)
    
    for item in skill_files:
        relative_path = item['path'][len(skill_path)+1:]  # 去掉前缀
        file_path = install_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = download_file(owner, repo, item['path'], branch)
        if content is None:
            print(f"❌ 下载失败: {item['path']}")
            return False
        
        file_path.write_bytes(content)
    
    print(f"✅ {skill_name} 安装成功!")
    print(f"   位置: {install_dir}")
    print(f"   版本: {skill_info.get('version', 'unknown')}")
    
    # 如果是项目级安装，更新index.json
    if location == "local":
        update_local_index(skill_name, skill_info, install_dir)
    
    return True


def update_local_index(skill_name: str, skill_info: Dict, install_dir: Path):
    """更新本地项目级技能索引"""
    index_file = Path(".agents") / "index.json"
    
    index = {"version": "1.0.0", "skills": {}}
    if index_file.exists():
        try:
            index = json.loads(index_file.read_text())
        except:
            pass
    
    index['skills'][skill_name] = {
        "name": skill_name,
        "version": skill_info.get('version', 'unknown'),
        "installed_at": str(install_dir),
        "source": "YidaSkillHub"
    }
    
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))


def list_installed_skills():
    """列出已安装的技能"""
    print("\n📂 已安装技能:\n")
    
    # 全局技能
    global_dir = Path.home() / ".agents" / "skills"
    if global_dir.exists():
        global_skills = [d.name for d in global_dir.iterdir() if d.is_dir()]
        if global_skills:
            print("【全局】~/.agents/skills/")
            for name in sorted(global_skills):
                print(f"  ✓ {name}")
            print()
    
    # 项目级技能
    local_dir = Path(".agents") / "skills"
    if local_dir.exists():
        local_skills = [d.name for d in local_dir.iterdir() if d.is_dir()]
        if local_skills:
            print(f"【项目级】{local_dir}")
            for name in sorted(local_skills):
                print(f"  ✓ {name}")
            print()
    
    if not global_dir.exists() and not local_dir.exists():
        print("  暂无已安装技能\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='YidaSkillHub 辅助工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    subparsers.add_parser('init', help='初始化配置')
    
    # list-remote 命令
    parser_list = subparsers.add_parser('list-remote', help='列出远程可用技能')
    parser_list.add_argument('--owner', default='logda', help='仓库所有者')
    parser_list.add_argument('--repo', default='YidaSkillHub', help='仓库名')
    parser_list.add_argument('--branch', default='main', help='分支')
    
    # install 命令
    parser_install = subparsers.add_parser('install', help='安装技能')
    parser_install.add_argument('skill', help='技能名称')
    parser_install.add_argument('--location', choices=['global', 'local'], required=True,
                               help='安装位置: global(~/.agents/skills/) 或 local(./.agents/skills/)')
    parser_install.add_argument('--owner', default='logda', help='仓库所有者')
    parser_install.add_argument('--repo', default='YidaSkillHub', help='仓库名')
    parser_install.add_argument('--branch', default='main', help='分支')
    
    # list-local 命令
    subparsers.add_parser('list-local', help='列出已安装技能')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        return init_config()
    
    elif args.command == 'list-remote':
        return list_available_skills(args.owner, args.repo, args.branch)
    
    elif args.command == 'install':
        return install_skill(args.skill, args.location, args.owner, args.repo, args.branch)
    
    elif args.command == 'list-local':
        return list_installed_skills()
    
    else:
        parser.print_help()
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
