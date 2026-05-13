# NekoCafé Monorepo Skeleton

实验二到实验四的统一代码仓库骨架。

## 当前范围

- 可运行服务：
  - `services/reservation`
  - `services/member`
- 设计层保留上下文：
  - `BC-ORDER`
  - `BC-STORE-OPS`
  - `BC-CAT-HEALTH`
  - `BC-RECOMMENDATION`

## 目录

- `services/`: 服务入口与各自实现
- `libs/common/`: 跨服务共享常量与约定
- `tests/`: 单元、集成、契约、E2E、性能测试占位
- `infra/`: Docker、Helm、可观测性配置占位
- `docs/`: ADR、运行手册、回滚手册

## 本地开发

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

## 下一步

1. 在实验一完成需求基线与命名体系。
2. 在实验二补齐上下文映射、C4、OpenAPI 与 ADR。
3. 在实验三把两个核心服务做成可容器化 PoC。
4. 在实验四把测试、质量门禁和 AI 评审挂到同一仓库。
