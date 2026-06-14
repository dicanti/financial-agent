import akshare as ak
import polars as pl
from akshare import stock_zh_ah_name

# 下载2023年年报数据
df_pd = ak.stock_yjbb_em(date="20231231")
df = pl.from_pandas(df_pd)

print(df.columns)

df = df.select([
    "股票简称","所处行业","净资产收益率","营业总收入-营业总收入","营业总收入-同比增长"
]).rename({
    "股票简称":"name",
    "所处行业":"industry",
    "净资产收益率":"roe",
    "营业总收入-营业总收入":"revenue",
    "营业总收入-同比增长":"revenue_yoy"
})
#print(df.head(3))
#print(df["industry"].null_count())   # 看有多少个null
#print(df["industry"].unique().to_list())  # 看有哪些唯一值
#df = df.with_column()
#print(df.null_count())
#print(df.filter(pl.col("roe") < 0))
#print(df.filter(pl.col("roe") >100))
#print(df["revenue_yoy"].describe())
print("\n" + "="*40)
baijiu = df.filter(pl.col("industry").str.contains("白酒"))
top5 =baijiu.filter(
    pl.col("roe").is_not_null()
).sort("roe",descending=True).head(5)
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

table = top5.to_pandas().to_markdown(index=False)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一位资深白酒行业分析师"},
        {"role": "user", "content": f"以下是目前A股白酒股中ROE最高的5家公司：\n\n{table}\n\n请分析：\n1. 这些公司的核心竞争力\n2. 白酒行业的竞争格局\n3. 投资者需要关注的风险因素"}
    ]
)

print(response.choices[0].message.content)