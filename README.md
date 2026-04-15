# YidaSkillHub

个人技能仓库，用于管理和分发自定义AI技能。

## 仓库结构

```
YidaSkillHub/
├── manifest.json              # 技能清单（自动生成）
├── update-manifest.py         # 自动生成 manifest.json 的脚本
├── README.md                  # 本文件
└── skills/                    # 所有技能（手动维护）
    └── find-yidaskill/        # 技能管理工具
        ├── SKILL.md           # 技能定义
        └── scripts/
            └── yidaskill.py   # 辅助脚本
```

## manifest.json

技能清单文件，**完全由 `skills/` 目录自动生成**，只包含核心信息：

```json
{
  "skills": {
    "find-yidaskill": {
      "name": "find-yidaskill",
      "description": "从YidaSkillHub发现和管理技能",
      "path": "skills/find-yidaskill",
      "tags": ["skill", "management"]
    }
  }
}
```

**注意**：manifest.json 不包含版本号，版本管理完全由 Git 负责。

## 添加新技能

1. 在 `skills/` 目录下创建新目录
2. 添加 `SKILL.md` 文件（遵循技能格式规范）
3. 运行 `python update-manifest.py` 自动生成 `manifest.json`
4. 提交并推送到GitHub

## 使用方式

1. 将本仓库安装到 Claude Code：
   ```bash
   # 克隆到本地
   git clone https://github.com/yida/YidaSkillHub.git
   
   # 安装 find-yidaskill 到全局
   cp -r YidaSkillHub/skills/find-yidaskill ~/.agents/skills/
   ```

2. 然后对 Claude 说：
   - "初始化yidaskill" - 设置配置
   - "找技能" - 查看可用技能
   - "安装 xxx" - 安装技能

## 辅助脚本

`find-yidaskill/scripts/yidaskill.py` 提供了命令行工具：

```bash
# 初始化配置
python yidaskill.py init

# 列出远程可用技能
python yidaskill.py list-remote

# 安装技能到全局
python yidaskill.py install find-yidaskill --location global

# 安装技能到项目
python yidaskill.py install find-yidaskill --location local

# 列出已安装技能
python yidaskill.py list-local
```

## 许可证

MIT
