---
name: find-yidaskill
description: |
  从YidaSkillHub发现、安装和更新个人技能。当用户说"找技能"、
  "安装技能"、"更新技能"、"初始化yidaskill"、
  "管理技能"或类似意图时触发。支持从GitHub的YidaSkillHub仓库
  发现可用技能，并安装到全局(~/.agents/skills)或项目级(./.agents/skills)。
---

# find-yidaskill

管理个人技能仓库 YidaSkillHub 中的技能。

## 配置

配置文件位置：`~/.YidaSkillHub/config.yaml`

如果不存在，首次使用时会自动创建。

**配置格式：**
```yaml
vault:
  url: "github:yida/YidaSkillHub"  # GitHub仓库地址
  branch: "main"                    # 分支名

settings:
  default_install_location: "ask"   # ask | global | local
  auto_update_check: true
```

## 核心功能

### 1. 初始化 YidaSkillHub

当用户说"初始化yidaskill"、"设置yidaskill"、"配置yidaskill"时：

1. 创建配置目录 `~/.YidaSkillHub/`
2. 创建默认配置文件 `~/.YidaSkillHub/config.yaml`
3. 创建本地技能存储目录 `~/.YidaSkillHub/local-skills/`
4. 告诉用户配置完成，并说明如何修改配置

### 2. 发现技能

当用户说"找技能"、"查看技能"、"有哪些技能"、"列出技能"时：

1. 读取配置文件获取仓库地址
2. 使用GitHub API获取 `manifest.json`：
   ```
   GET https://raw.githubusercontent.com/{owner}/{repo}/{branch}/manifest.json
   ```
3. 解析manifest，列出所有可用技能：
   - 技能名称
   - 描述
   - 路径
   - 标签（如有）
4. 询问用户是否要安装某个技能

### 3. 安装技能

当用户说"安装xxx技能"、"添加xxx"、"给我装上xxx"时：

**步骤：**

1. **确认安装位置**：询问用户
   - "安装到全局 (~/.agents/skills/)？所有项目都能用"
   - "还是安装到项目级 (./.agents/skills/)？仅当前项目可用"

2. **检查manifest**：确认技能存在

3. **获取技能文件列表**：
   ```
   GET https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1
   ```
   筛选出 `skills/{skill-name}/` 下的所有文件

4. **下载文件**：
   对每个文件：
   ```
   GET https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filepath}
   ```

5. **保存到目标位置**：
   - 全局：`~/.agents/skills/{skill-name}/`
   - 项目级：`./.agents/skills/{skill-name}/`

6. **更新索引**：
   - 如果是项目级，更新 `./.agents/index.json`

7. **报告结果**：
   - 安装成功
   - 安装位置
   - 可用命令/下一步

### 4. 更新技能

当用户说"更新xxx技能"、"升级xxx"、"重新安装xxx"时：

1. 检查本地是否已安装该技能
2. 询问用户确认重新下载
3. 从GitHub重新下载并覆盖
4. 报告更新结果

**注意**：manifest.json 不包含版本号，版本管理完全由 Git 负责。

## 文件结构

**GitHub仓库结构：**
```
YidaSkillHub/
├── manifest.json              # 技能清单
└── skills/
    ├── find-yidaskill/        # 本技能
    │   ├── SKILL.md
    │   └── scripts/
    └── other-skill/
        └── SKILL.md
```

**本地项目级结构：**
```
project/
├── .agents/
│   ├── skills/                # 项目级技能
│   │   └── some-skill/
│   └── index.json             # 本地索引
└── src/...
```

**manifest.json格式（简洁版，无版本号，Git管理版本）：**
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

## 交互示例

**初始化：**
```
用户: 初始化yidaskill
Claude: 
✅ YidaSkillHub 初始化完成！

配置文件已创建: ~/.YidaSkillHub/config.yaml
你可以修改它来自定义行为。

现在你可以：
- "找技能" - 查看可用的技能
- "安装 xxx" - 安装某个技能
```

**发现技能：**
```
用户: 找技能
Claude:
📦 YidaSkillHub 可用技能:

1. find-yidaskill
   从YidaSkillHub发现和管理技能
   标签: skill, management

2. web-automation
   网页自动化测试与抓取
   标签: browser, testing

要安装某个技能，说"安装 xxx"
```

**安装技能：**
```
用户: 安装 web-automation
Claude:
你想把 web-automation 安装到哪里？

1. 全局 (~/.agents/skills/) - 所有项目可用
2. 项目级 (./.agents/skills/) - 仅当前项目

请选择 [1/2]: 

[用户选择后]
📥 正在下载 web-automation...
✅ 安装完成！

位置: ~/.agents/skills/web-automation/

现在你可以使用 web-automation 技能了。
```

## 错误处理

- **网络错误**：提示检查网络，建议重试
- **技能不存在**：列出可用技能，询问是否正确拼写
- **权限错误**：检查目录权限，必要时使用sudo（全局安装）
- **已存在**：询问是否覆盖或跳过

## 注意事项

1. 始终询问用户安装位置（全局vs项目级）
2. 安装前检查是否已存在同名技能
3. 下载过程中显示进度或至少显示"正在下载"
4. 所有操作完成后给出明确反馈
