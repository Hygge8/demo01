# 数据说明

9 个 CSV 位于 `data/raw/`。本次目录整理保留原始文件名、字段名和文件内容。

| 文件 | 内容 | 主要关联字段 |
| --- | --- | --- |
| `olist_customers_dataset.csv` | 客户 | `customer_id`、`customer_unique_id` |
| `olist_orders_dataset.csv` | 订单及状态、时间 | `order_id`、`customer_id` |
| `olist_order_items_dataset.csv` | 订单商品明细 | `order_id`、`product_id`、`seller_id` |
| `olist_order_payments_dataset.csv` | 支付明细 | `order_id` |
| `olist_order_reviews_dataset.csv` | 评分与评论 | `order_id`、`review_id` |
| `olist_products_dataset.csv` | 商品属性 | `product_id`、`product_category_name` |
| `olist_sellers_dataset.csv` | 卖家 | `seller_id` |
| `olist_geolocation_dataset.csv` | 邮编及地理位置 | `geolocation_zip_code_prefix` |
| `product_category_name_translation.csv` | 商品类别英文名称 | `product_category_name` |

表的字段顺序、CSV 记录数、字节数和 SHA-256 存于 [manifest.json](manifest.json)，作为仓库原始文件的完整性基线。它描述文件完整性，不验证订单业务规则或所有表的关联关系。

## 读取约定

- 编码：UTF-8；读取时使用 `newline=""`，让 CSV 解析器处理换行。
- 客户、卖家、商品及订单 ID 按字符串读取；邮编前缀也按字符串处理，保留前导零。
- 评论标题和正文可能为空，也可能包含逗号和换行。
- 同一订单可有多条商品、支付和评论记录；合并前先确定需要的粒度。
- 地理位置表的邮编可能重复；连接前先检查并按分析目的聚合。
- 商品字段中 `product_name_lenght`、`product_description_lenght` 为原始拼写，读取代码应使用这些名称。

## 检查

```bash
python scripts/validate_data.py          # 全量：表头、大小、记录宽度、记录数、SHA-256
python scripts/validate_data.py --quick  # 快速：文件存在、大小、表头
```

检查器逐条读取数据，避免把所有 CSV 一次性载入内存。输出仅包含校验摘要和错误位置。
