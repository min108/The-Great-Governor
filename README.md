# 监督智源

集团大监督业务资产的演示环境，供党风廉政办、党委巡视办看资产如何归集、适用和回头看。界面名称是「监督智源」。

四类资产分开存放：数据标准、监督要求、分析思路、经验。业务明细仍留在源系统，这里只保留对照和调阅路径。案例使用示例单位和化名，不把真实子公司写成查实对象。

## 本地运行

```bash
cd backend
pip install -r requirements.txt
python3 -m app.seed
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://127.0.0.1:5173 。建议先从全貌进入「化整为零规避招标」，再打开「梳理采购工作要求」，看质量关为什么拦住发布。

密钥只放在仓库根目录、已被忽略的 `.env` 里，变量名 `DEEPSEEK_API_KEY`，可参考 `.env.example`。没有密钥时，已入库的梳理和按段落的拆解仍然可以演示。不要把密钥写入仓库。

数据库在 `backend/data/`，不入库。需要整库重做时，在 `backend` 下执行 `python3 -m app.seed`。
