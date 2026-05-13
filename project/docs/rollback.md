# Rollback Guide

## 当前适用范围

本文档适用于 NekoCafé 单体实现阶段，也就是“一个应用承载页面、接口和 SQLite 数据”的阶段。

## 当前回滚策略

1. 代码回滚：
   - 优先回退到最近一个通过 `pytest -q` 的 Git 提交
2. 数据回滚：
   - 本地 PoC 使用 SQLite，可删除 `data/nekocafe.sqlite3` 重新生成种子数据
3. 容器回滚：
   - 回退到最近一个可通过 `docker compose up --build` 的提交

## 常见恢复动作

- 页面异常：
  - 回滚 `app/templates/` 与 `app/static/`
- 接口异常：
  - 回滚 `app/main.py` 与 `app/data.py`
- 演示数据异常：
  - 删除 SQLite 文件后重新访问应用

## 当前限制

当前阶段尚未接入：

- 自动化发布回滚
- 灰度流量切分
- 基于监控阈值的自动回退
