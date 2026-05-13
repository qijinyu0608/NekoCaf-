# NekoCafé Course Project

统一工作区，用于承接《软件工程》课程四次连贯实验的工程文件、共享基线与最终提交物。

## 目录说明

- `docs/foundation/`: 跨实验共享基线，作为后续所有文档的统一事实源。
- `docs/lab1` ~ `docs/lab4`: 每次实验自己的源文件、图稿、导出件和提交件。
- `docs/product/`: 当前有效 PRD 与产品实现说明。
- `project/`: Python monorepo，承接实验二到实验四的设计、实现、测试与 DevOps 落地。
- `assets/`: 截图、视频脚本素材、过程证据。
- `templates/`: 从课程原始模板复制出的工作副本，不修改老师原件。
- `scripts/`: 生成基础 Word/Excel 文档的脚本。

## 使用顺序

1. 先维护 `docs/foundation/` 中的共享基线。
2. 再将共享基线映射到 `docs/lab1` 的正式交付物。
3. 按 `docs/lab2 -> docs/lab3 -> docs/lab4` 的课程要求继续推进连续实验。
4. 实验二到实验四继续引用同一套需求 ID、术语、追溯矩阵和服务命名。
5. `project/` 中以当前单体实现为主线持续迭代顾客预约与店员后台核心闭环。

## 常用动作

- 生成基础 Word/Excel：运行 `scripts/` 下的构建脚本。
- 运行项目测试：在 `project/` 下执行 `pytest`。
- 整理每次实验提交物：将最终版本归档到各 `docs/labX/submission/`。
- Git 提交信息必须遵循 `Conventional Commits`，阶段完成后补对应实验 tag。

## 文档红线

- 所有通过 `scripts/` 生成的 Word 文档必须统一使用黑色字体，不允许出现 Word 主题默认的蓝色标题。
- `Normal`、`Title`、`Heading`、列表样式统一走 `scripts/docx_style_policy.py`，后续实验文档继续复用这条规则。
