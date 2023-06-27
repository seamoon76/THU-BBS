# THUBBS-backend

马骐 软件01 2019011844 ；余欣然 软件03 2020012393；贾奕翔 软件03 2020012399

## 配置

1. 安装 Python版本 11 以上
2. 用conda或者pip安装 `requirements.txt` 里的库

## 启动方式

主服务启动
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --log-level warning
```
雪花ID服务启动
```bash
snowflake_start_server --port=8910
```
