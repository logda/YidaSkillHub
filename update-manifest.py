#!/usr/bin/env python3
"""
YidaSkillHub Manifest 更新脚本
自动扫描 skills/ 目录，更新 manifest.json
"""

import os
import sys
import json
import re
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """解析 SKILL.md 的 YAML frontmatter，支持多行字符串"""
    # 匹配 --- 包围的 frontmatter
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return {}
    
    frontmatter = match.group(1)
    result = {}
    current_key = None
    current_value_lines = []
    
    lines = frontmatter.strip().split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 跳过注释和空行
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # 检查是否是新的 key: value 行
        if ':' in stripped and not stripped.startswith('-'):
            # 保存之前的 key-value
            if current_key:
                value = ' '.join(current_value_lines).strip()
                result[current_key] = value
            
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # 如果是多行字符串开始标记 (| 或 >)
            if value in ('|', '>'):
                current_key = key
                current_value_lines = []
                i += 1
                # 读取后续缩进的行
                while i < len(lines):
                    next_line = lines[i]
                    # 检查是否是新 key 或结束
                    if next_line.strip() and ':' in next_line and not next_line.startswith(' ') and not next_line.startswith('\t'):
                        break
                    # 收集非空行
                    if next_line.strip():
                        current_value_lines.append(next_line.strip())
                    i += 1
                continue
            else:
                # 普通单行 value
                result[key] = value.strip('"\'')
                current_key = None
                current_value_lines = []
        
        i += 1
    
    # 保存最后一个 key-value
    if current_key and current_value_lines:
        value = ' '.join(current_value_lines).strip()
        result[current_key] = value
    
    return result


def scan_skills(skills_dir: Path) -> dict:
    """扫描 skills/ 目录，读取所有 SKILL.md - 不包含 version，完全由 Git 管理版本"""
    skills = {}
    
    if not skills_dir.exists():
        print(f"❌ 目录不存在: {skills_dir}")
        return skills
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"⚠️  跳过 {skill_dir.name}: 没有 SKILL.md")
            continue
        
        content = skill_md.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)
        
        if not frontmatter:
            print(f"⚠️  跳过 {skill_dir.name}: 无法解析 frontmatter")
            continue
        
        name = frontmatter.get('name', skill_dir.name)
        
        # 只保留核心字段，version 由 Git 管理
        skills[name] = {
            "name": name,
            "description": frontmatter.get('description', '无描述').replace('\n', ' '),
            "path": f"skills/{skill_dir.name}"
        }
        
        # 可选字段
        tags_str = frontmatter.get('tags', '')
        if tags_str:
            tags_str = tags_str.strip('[]')
            skills[name]["tags"] = [t.strip() for t in tags_str.split(',') if t.strip()]
    
    return skills


def update_manifest(repo_dir: Path, new_skills: dict) -> dict:
    """更新 manifest.json - 严格同步 skills/ 目录，只包含 skills 数据"""
    manifest_path = repo_dir / "manifest.json"
    
    # 读取现有 manifest（仅用于对比）
    old_skills = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                old_manifest = json.load(f)
                old_skills = old_manifest.get('skills', {})
        except Exception:
            pass
    
    # 统计变更
    added = []
    updated = []
    removed = []
    unchanged = []
    
    # 检查新增和更新
    for name, info in new_skills.items():
        if name not in old_skills:
            added.append(name)
        elif old_skills[name] != info:  # 完整对象对比
            updated.append(name)
        else:
            unchanged.append(name)
    
    # 检查删除
    for name in old_skills:
        if name not in new_skills:
            removed.append(name)
    
    # 构建新的 manifest - 只包含 skills，完全由目录决定
    manifest = {"skills": new_skills}
    
    return manifest, added, updated, removed, unchanged


def main():
    """主函数"""
    # 确定仓库目录（脚本所在目录）
    script_dir = Path(__file__).parent.resolve()
    skills_dir = script_dir / "skills"
    manifest_path = script_dir / "manifest.json"
    
    print("🔍 扫描技能目录...")
    print(f"   路径: {skills_dir}")
    print()
    
    # 扫描技能
    new_skills = scan_skills(skills_dir)
    
    if not new_skills:
        print("❌ 未发现任何技能")
        return 1
    
    print(f"✅ 发现 {len(new_skills)} 个技能")
    print()
    
    # 更新 manifest
    manifest, added, updated, removed, unchanged = update_manifest(script_dir, new_skills)
    
    # 显示变更报告
    print("📊 变更报告:")
    print()
    
    if added:
        print(f"  ➕ 新增 ({len(added)}):")
        for name in added:
            print(f"     • {name}")
        print()
    
    if updated:
        print(f"  📝 内容更新 ({len(updated)}):")
        for name in updated:
            print(f"     • {name}")
        print()
    
    if removed:
        print(f"  🗑️  已移除 ({len(removed)}):")
        for name in removed:
            print(f"     • {name}")
        print()
    
    if unchanged:
        print(f"  ✅ 未变更 ({len(unchanged)}):")
        for name in unchanged:
            print(f"     • {name}")
        print()
    
    # 写入 manifest.json
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"💾 manifest.json 已更新: {manifest_path}")
    print()
    print("下一步:")
    print("  1. 检查变更: git diff manifest.json")
    print("  2. 提交推送: git add . && git commit -m 'Update manifest' && git push")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
