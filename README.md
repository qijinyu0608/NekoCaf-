# NekoCafé Course Project

统一工作区，用于承接《软件工程》课程四次连贯实验的工程文件、共享基线与最终提交物。

## 目录说明

- `docs/foundation/`: 跨实验共享基线，作为后续所有文档的统一事实源。
- `docs/lab1` ~ `docs/lab4`: 每次实验自己的源文件、图稿、导出件和提交件。
- `project/`: Python monorepo，承接实验二到实验四的设计、实现、测试与 DevOps 落地。
- `assets/`: 截图、视频脚本素材、过程证据。
- `templates/`: 从课程原始模板复制出的工作副本，不修改老师原件。
- `scripts/`: 生成基础 Word/Excel 文档的脚本。

## 使用顺序

1. 先维护 `docs/foundation/` 中的共享基线。
2. 再将共享基线映射到 `docs/lab1` 的正式交付物。
3. 实验二到实验四继续引用同一套需求 ID、术语、追溯矩阵和服务命名。
4. `project/` 中只优先实现 `reservation` 与 `member` 两个核心服务，其他上下文先保留在设计层。

## 常用动作

- 生成基础 Word/Excel：运行 `scripts/` 下的构建脚本。
- 运行项目测试：在 `project/` 下执行 `pytest`。
- 整理每次实验提交物：将最终版本归档到各 `docs/labX/submission/`。
