# Snail - 法律数据采集工具集

## 目录用途

本目录存放婚姻家庭法律咨询 Agent 项目所需的所有数据采集（爬虫）相关文件，包括爬虫脚本、配置、日志和辅助工具模块。

## 目录结构

```
Snail/
├── __init__.py              # 包初始化
├── config.py                # 爬虫全局配置（请求头、超时、代理等）
├── README.md                # 本文件
├── spiders/                 # 爬虫脚本目录
│   ├── __init__.py
│   ├── law_spider.py        # 法律条文爬虫（国家法律法规数据库等）
│   ├── judicial_spider.py   # 司法解释爬虫（最高法官网等）
│   └── case_spider.py       # 裁判案例爬虫（人民法院案例库等）
├── utils/                   # 工具模块目录
│   ├── __init__.py
│   ├── validator.py         # 文件格式验证与错误处理
│   ├── logger.py            # 日志配置模块
│   └── request_helper.py    # HTTP 请求辅助（重试、限速、UA轮换）
└── logs/                    # 运行日志目录
    └── .gitkeep
```

## 文件命名规则

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 爬虫脚本 | `{数据类别}_spider.py` | `law_spider.py` |
| 工具模块 | `{功能描述}.py` | `validator.py` |
| 配置文件 | `config.py` 或 `config.json` | `config.py` |
| 日志文件 | `{爬虫名}_{YYYYMMDD}.log` | `law_spider_20260427.log` |

## 格式要求

- 爬虫脚本必须使用 Python 3.11+ 语法
- 所有爬虫脚本必须导入 `utils.validator` 模块，通过 `save_to_collected_data()` 保存文件
- 禁止直接将文件写入 `Collected legal data` 目录，必须经过验证模块
- 日志文件使用 UTF-8 编码

## 特殊处理说明

### 反爬虫策略

1. **请求频率控制**：所有爬虫必须设置请求间隔（默认 3-5 秒），避免触发目标网站频率限制
2. **User-Agent 轮换**：通过 `utils/request_helper.py` 自动轮换 UA
3. **自动重试**：网络错误自动重试 3 次，指数退避
4. **代理支持**：如需代理，在 `config.py` 中配置

### 合规要求

1. **遵守 robots.txt**：爬虫启动前必须检查目标网站 robots.txt
2. **不突破安全防护**：禁止绕过验证码、加密参数等安全机制
3. **数据脱敏**：裁判案例必须移除当事人真实姓名、身份证号等个人信息
4. **版权尊重**：仅采集公开法律数据，不搬运商业数据库的评析内容

### 日志规范

- 每次运行自动创建日志文件到 `logs/` 目录
- 日志级别：INFO（正常流程）、WARNING（被拒绝的文件）、ERROR（异常）
- 日志保留 30 天，超期自动清理
