---
title: pandas
---
## reading csv
### pandas library
#### pd.read_csv (from pandas library)
- Library: Part of the pandas library; need to install pandas.
- Data Structure: Reads data into a **DataFrame**, a 2D tabular data structure.
- Memory: Reads the **entire file into memory** (though you can read in chunks).
- Data Types: **Infers data types automatically**.
- Functionality: Provides extensive functionalities like handling missing values, reading from a URL, specifying data types, etc.
- Index: Can automatically assign an index.
- API Complexity: More complex with many optional parameters.
- Flexibility: **Highly flexible** for handling various types of data.
- Speed: **Generally faster** for data manipulation tasks as it's built on top of NumPy.
#### sample code
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import argparse


def save_csv_to_db(input_csv):
    # Connect to the PostgreSQL database
    engine = create_engine(
        "postgresql+psycopg2://skopenai:!skcc1234@infratf-db.postgres.database.azure.com:5432/chatbot?sslmode=allow"
    )

    # Create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv, dtype=str)
    df.where(pd.notna(df), None, inplace=True)

    # Loop through the DataFrame and add each row to the database
    for index, row in df.iterrows():
        # print("----------------------------------------------------------------")
        # print(f"Row data: {row}")
        try:
            # Your table class definition might differ. Make sure to match it accordingly.
            corp_info_instance = CorpInfo(
                corp_code=row["corp_code"],
                corp_name=row["corp_name"],
                corp_name_eng=row["corp_name_eng"],
                stock_name=row["stock_name"],
                stock_code=row["stock_code"],
                ceo_nm=row["ceo_nm"],
                corp_cls=row["corp_cls"],
                jurir_no=row["jurir_no"],
                bizr_no=row["bizr_no"],
                adres=row["adres"],
                hm_url=row["hm_url"],
                ir_url=row["ir_url"],
                phn_no=row["phn_no"],
                fax_no=row["fax_no"],
                induty_code=row["induty_code"],
                est_dt=row["est_dt"],
                acc_mt=row["acc_mt"],
                # logo_img_url=row['logo_img_url']  # Assuming this field is not in your CSV
            )
            session.add(corp_info_instance)
            # Commit the changes
            session.commit()
        except Exception as e:
            print("----------------------------------------------------------------")
            print(f"Error occurred while processing row {index}: {e}")
            print(f"Row data: {row}")
            print("----------------------------------------------------------------")
            session.rollback()
            return


# Define your SQLAlchemy CorpInfo class to mirror the database table structure.
Base = declarative_base()


class CorpInfo(Base):
    __tablename__ = "corp_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(8))
    corp_name = Column(String)
    corp_name_eng = Column(String)
    stock_name = Column(String)
    stock_code = Column(String(6))
    ceo_nm = Column(String)
    corp_cls = Column(String(1))
    jurir_no = Column(String(13))
    bizr_no = Column(String)
    adres = Column(String)
    hm_url = Column(String)
    ir_url = Column(String)
    phn_no = Column(String(25))
    fax_no = Column(String(25))
    induty_code = Column(String(10))
    est_dt = Column(String(8))
    acc_mt = Column(String(2))
    # logo_img_url = Column(String)  # Assuming this field is not in your CSV


parser = argparse.ArgumentParser(description="Save CSV to Database.")
parser.add_argument("input_csv", help="Path to the input CSV file.")

# Run the function
if __name__ == "__main__":
    args = parser.parse_args()
    save_csv_to_db(args.input_csv)
```
#### 주의!!
파이썬의 NaN은 문자 그대로 DB에 "NaN"으로 저장됨. 이것을 None으로 바꿔야 DB에 저장할 때 Null으로 저장. 위 sample code에 df.where(pd.notna(df), None, inplace=True)라고 되어 있는 부분.
### standart library csv
#### csv.DictReader (from the csv standard library)
- Library: Part of Python's standard library, so no need to install external packages.
- Data Structure: Reads data into an **OrderedDict** for each row.
- Memory: Suitable for large files as it reads the file **row-by-row**.
- Data Types: Does not infer data types; treats everything as a **string**.
- Functionality: Provides basic CSV reading capabilities.
- Index: Does not automatically assign an index.
- API Complexity: Simple, not many features.
- Flexibility: **Less flexible** when it comes to reading different date formats, handling missing values, etc.
- Speed: **Generally slower** for data manipulation tasks due to being pure Python.
#### sample code
```python
import csv
import argparse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class FinancialReportBase(Base):
    __tablename__ = "financial_report_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rcept_no = Column(String(14))
    reprt_code = Column(String(5))
    bsns_year = Column(String(4))
    corp_code = Column(String(8))
    sj_div = Column(String(3))
    sj_nm = Column(String)
    account_id = Column(String)
    account_nm = Column(String)
    account_detail = Column(String)
    thstrm_nm = Column(String)
    thstrm_amount = Column(BigInteger)
    frmtrm_nm = Column(String(255))
    frmtrm_amount = Column(BigInteger)
    ord = Column(Integer)
    currency = Column(String(3))
    report_type = Column(String(1))


class FinancialQuarterlyReport(Base):
    __tablename__ = "financial_quaterly_report"
    id = Column(Integer, ForeignKey("financial_report_base.id"), primary_key=True)
    frmtrm_q_nm = Column(String)
    frmtrm_q_amount = Column(BigInteger)
    frmtrm_add_amount = Column(BigInteger)


class FinancialAnnualReport(Base):
    __tablename__ = "financial_annual_report"
    id = Column(Integer, ForeignKey("financial_report_base.id"), primary_key=True)
    bfefrmtrm_nm = Column(String)
    bfefrmtrm_amount = Column(BigInteger)


def save_csv_to_db(input_csv, report_type):
    engine = create_engine("your database connection string here")
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(input_csv, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            base_report = FinancialReportBase(
                rcept_no=row["rcept_no"],
                reprt_code=row["reprt_code"],
                bsns_year=row["bsns_year"],
                corp_code=row["corp_code"],
                sj_div=row["sj_div"],
                sj_nm=row["sj_nm"],
                account_id=row["account_id"],
                account_nm=row["account_nm"],
                account_detail=row["account_detail"],
                thstrm_nm=row["thstrm_nm"],
                thstrm_amount=int(row["thstrm_amount"]),
                frmtrm_nm=row["frmtrm_nm"],
                frmtrm_amount=int(row["frmtrm_amount"]),
                ord=int(row["ord"]),
                currency=row["currency"],
                report_type=report_type,
            )
            session.add(base_report)
            session.flush()  # to get the id of base_report

            if report_type == "Q":
                quarter_report = FinancialQuarterlyReport(
                    id=base_report.id,
                    frmtrm_q_nm=row.get("frmtrm_q_nm", None),
                    frmtrm_q_amount=int(row.get("frmtrm_q_amount", 0)),
                    frmtrm_add_amount=int(row.get("frmtrm_add_amount", 0)),
                )
                session.add(quarter_report)
            elif report_type == "A":
                annual_report = FinancialAnnualReport(
                    id=base_report.id,
                    bfefrmtrm_nm=row.get("bfefrmtrm_nm", None),
                    bfefrmtrm_amount=int(row.get("bfefrmtrm_amount", 0)),
                )
                session.add(annual_report)
            session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save CSV to Database.")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument(
        "report_type",
        help="Type of the report, either 'Q' for Quarterly or 'A' for Annual",
    )
    args = parser.parse_args()

    save_csv_to_db(args.input_csv, args.report_type)
```
### save to DB
#### bulk data insert
#### int64 preprocessing
#### sample
##### sample data
```python
rcept_no,reprt_code,bsns_year,corp_code,sj_div,sj_nm,account_id,account_nm,account_detail,thstrm_nm,thstrm_amount,frmtrm_nm,frmtrm_amount,ord,currency,thstrm_add_amount,frmtrm_q_nm,frmtrm_q_amount,frmtrm_add_amount
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_CurrentAssets,유동자산,-,제 52 기 반기말,71148585000000,제 51 기말,72659080000000,1,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_CashAndCashEquivalents,현금및현금성자산,-,제 52 기 반기말,3039195000000,제 51 기말,2081917000000,2,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_ShortTermDepositsNotClassifiedAsCashEquivalents,단기금융상품,-,제 52 기 반기말,24505262000000,제 51 기말,26501392000000,3,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_ShortTermTradeReceivable,매출채권,-,제 52 기 반기말,26595759000000,제 51 기말,26255438000000,4,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_ShortTermOtherReceivables,미수금,-,제 52 기 반기말,1787124000000,제 51 기말,2406795000000,5,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,선급금,-,제 52 기 반기말,888491000000,제 51 기말,908288000000,6,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,선급비용,-,제 52 기 반기말,885612000000,제 51 기말,813651000000,7,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_Inventories,재고자산,-,제 52 기 반기말,12090721000000,제 51 기말,12201712000000,8,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_OtherCurrentAssets,기타유동자산,-,제 52 기 반기말,1356421000000,제 51 기말,1489887000000,9,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_NoncurrentAssets,비유동자산,-,제 52 기 반기말,147048817000000,제 51 기말,143521840000000,10,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,기타포괄손익-공정가치금융자산,-,제 52 기 반기말,1066255000000,제 51 기말,1206080000000,11,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,당기손익-공정가치금융자산,-,제 52 기 반기말,3181000000,제 51 기말,3181000000,12,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_InvestmentsInSubsidiariesJointVenturesAndAssociates,"종속기업, 관계기업 및 공동기업 투자",-,제 52 기 반기말,56636955000000,제 51 기말,56571252000000,13,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_PropertyPlantAndEquipment,유형자산,-,제 52 기 반기말,78296370000000,제 51 기말,74090275000000,14,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_IntangibleAssetsOtherThanGoodwill,무형자산,-,제 52 기 반기말,7401569000000,제 51 기말,8008653000000,15,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_DepositsForSeveranceInsurance,순확정급여자산,-,제 52 기 반기말,162303000000,제 51 기말,486855000000,16,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_DeferredTaxAssets,이연법인세자산,-,제 52 기 반기말,1300030000000,제 51 기말,547176000000,17,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_OtherNonCurrentAssets,기타비유동자산,-,제 52 기 반기말,2182154000000,제 51 기말,2608368000000,18,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_Assets,자산총계,-,제 52 기 반기말,218197402000000,제 51 기말,216180920000000,19,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_CurrentLiabilities,유동부채,-,제 52 기 반기말,37215802000000,제 51 기말,36237164000000,21,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,매입채무,-,제 52 기 반기말,8325371000000,제 51 기말,7547273000000,22,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_ShorttermBorrowings,단기차입금,-,제 52 기 반기말,9357803000000,제 51 기말,10228216000000,23,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,미지급금,-,제 52 기 반기말,7371397000000,제 51 기말,9142890000000,24,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,선수금,-,제 52 기 반기말,402663000000,제 51 기말,355562000000,25,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,예수금,-,제 52 기 반기말,316423000000,제 51 기말,383450000000,26,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,미지급비용,-,제 52 기 반기말,5718274000000,제 51 기말,5359291000000,27,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_CurrentTaxLiabilities,당기법인세부채,-,제 52 기 반기말,2372958000000,제 51 기말,788846000000,28,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,-표준계정코드 미사용-,유동성장기부채,-,제 52 기 반기말,104905000000,제 51 기말,153942000000,29,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_CurrentProvisions,충당부채,-,제 52 기 반기말,2913541000000,제 51 기말,2042039000000,30,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_OtherCurrentLiabilities,기타유동부채,-,제 52 기 반기말,332467000000,제 51 기말,235655000000,31,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_NoncurrentLiabilities,비유동부채,-,제 52 기 반기말,2231155000000,제 51 기말,2073509000000,32,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_BondsIssued,사채,-,제 52 기 반기말,41094000000,제 51 기말,39520000000,33,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_LongTermBorrowingsGross,장기차입금,-,제 52 기 반기말,152167000000,제 51 기말,174651000000,34,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_LongTermOtherPayablesGross,장기미지급금,-,제 52 기 반기말,1454341000000,제 51 기말,1574535000000,35,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_NoncurrentProvisions,장기충당부채,-,제 52 기 반기말,582282000000,제 51 기말,283508000000,36,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_OtherNonCurrentLiabilities,기타비유동부채,-,제 52 기 반기말,1271000000,제 51 기말,1295000000,37,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_Liabilities,부채총계,-,제 52 기 반기말,39446957000000,제 51 기말,38310673000000,38,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_IssuedCapital,자본금,-,제 52 기 반기말,897514000000,제 51 기말,897514000000,40,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_IssuedCapitalOfPreferredStock,우선주자본금,-,제 52 기 반기말,119467000000,제 51 기말,119467000000,41,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_IssuedCapitalOfCommonStock,보통주자본금,-,제 52 기 반기말,778047000000,제 51 기말,778047000000,42,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_SharePremium,주식발행초과금,-,제 52 기 반기말,4403893000000,제 51 기말,4403893000000,43,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_RetainedEarnings,이익잉여금(결손금),-,제 52 기 반기말,173306465000000,제 51 기말,172288326000000,44,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,dart_ElementsOfOtherStockholdersEquity,기타자본항목,-,제 52 기 반기말,142573000000,제 51 기말,280514000000,45,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_Equity,자본총계,-,제 52 기 반기말,178750445000000,제 51 기말,177870247000000,46,KRW,,,,
20200814001766,11012,2020,00126380,BS,재무상태표,ifrs-full_EquityAndLiabilities,부채와자본총계,-,제 52 기 반기말,218197402000000,제 51 기말,216180920000000,47,KRW,,,,
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_Revenue,수익(매출액),-,제 52 기 반기,37904100000000,,,0,KRW,77992039000000,제 51 기 반기,38149674000000,75188069000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_CostOfSales,매출원가,-,제 52 기 반기,26252598000000,,,1,KRW,55973547000000,제 51 기 반기,28690721000000,55142944000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_GrossProfit,매출총이익,-,제 52 기 반기,11651502000000,,,2,KRW,22018492000000,제 51 기 반기,9458953000000,20045125000000
20200814001766,11012,2020,00126380,IS,손익계산서,dart_TotalSellingGeneralAdministrativeExpenses,판매비와관리비,-,제 52 기 반기,7003528000000,,,3,KRW,14338175000000,제 51 기 반기,6661795000000,13351044000000
20200814001766,11012,2020,00126380,IS,손익계산서,dart_OperatingIncomeLoss,영업이익,-,제 52 기 반기,4647974000000,,,4,KRW,7680317000000,제 51 기 반기,2797158000000,6694081000000
20200814001766,11012,2020,00126380,IS,손익계산서,dart_OtherGains,기타수익,-,제 52 기 반기,220194000000,,,5,KRW,466563000000,제 51 기 반기,1587978000000,1843504000000
20200814001766,11012,2020,00126380,IS,손익계산서,dart_OtherLosses,기타비용,-,제 52 기 반기,238071000000,,,6,KRW,400991000000,제 51 기 반기,153617000000,338453000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_FinanceIncome,금융수익,-,제 52 기 반기,800092000000,,,7,KRW,2419361000000,제 51 기 반기,1565306000000,2208374000000
20200814001766,11012,2020,00126380,IS,손익계산서,-표준계정코드 미사용-,금융비용,-,제 52 기 반기,746609000000,,,8,KRW,2394042000000,제 51 기 반기,1492072000000,1948352000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_ProfitLossBeforeTax,법인세비용차감전순이익(손실),-,제 52 기 반기,4683580000000,,,9,KRW,7771208000000,제 51 기 반기,4304753000000,8459154000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_IncomeTaxExpenseContinuingOperations,법인세비용,-,제 52 기 반기,1161339000000,,,10,KRW,1943036000000,제 51 기 반기,241584000000,1307357000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_ProfitLossFromContinuingOperations,계속영업이익(손실),-,제 52 기 반기,3522241000000,,,11,KRW,5828172000000,제 51 기 반기,4063169000000,7151797000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_ProfitLoss,당기순이익(손실),-,제 52 기 반기,3522241000000,,,12,KRW,5828172000000,제 51 기 반기,4063169000000,7151797000000
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_BasicEarningsLossPerShare,기본주당이익(손실),-,제 52 기 반기,519,,,14,KRW,858,제 51 기 반기,598,1053
20200814001766,11012,2020,00126380,IS,손익계산서,ifrs-full_DilutedEarningsLossPerShare,희석주당이익(손실),-,제 52 기 반기,519,,,15,KRW,858,제 51 기 반기,598,1053
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,ifrs-full_ProfitLoss,당기순이익(손실),-,제 52 기 반기,3522241000000,,,0,KRW,5828172000000,제 51 기 반기,4063169000000,7151797000000
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,ifrs-full_OtherComprehensiveIncome,기타포괄손익,-,제 52 기 반기,204056000000,,,1,KRW,-137941000000,제 51 기 반기,-19304000000,58888000000
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,dart_OtherComprehensiveIncomeThatWillNotBeReclassifiedToProfitOrLossNetOfTax,후속적으로 당기손익으로 재분류되지 않는 포괄손익,-,제 52 기 반기,204056000000,,,2,KRW,-137941000000,제 51 기 반기,-19304000000,58888000000
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,-표준계정코드 미사용-,기타포괄손익-공정가치금융자산평가손익,-,제 52 기 반기,214544000000,,,3,KRW,-101373000000,제 51 기 반기,-6930000000,99627000000
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,-표준계정코드 미사용-,순확정급여자산 재측정요소,-,제 52 기 반기,-10488000000,,,4,KRW,-36568000000,제 51 기 반기,-12374000000,-40739000000
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,dart_OtherComprehensiveIncomeThatWillBeReclassifiedToProfitOrLossNetOfTax,후속적으로 당기손익으로 재분류되는 포괄손익,-,제 52 기 반기,0,,,5,KRW,0,제 51 기 반기,0,0
20200814001766,11012,2020,00126380,CIS,포괄손익계산서,ifrs-full_ComprehensiveIncome,총포괄손익,-,제 52 기 반기,3726297000000,,,6,KRW,5690231000000,제 51 기 반기,4043865000000,7210685000000
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_CashFlowsFromUsedInOperatingActivities,영업활동 현금흐름,-,제 52 기 반기,18085788000000,,,0,KRW,,제 51 기 반기,2228736000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,dart_ProfitLossForStatementOfCashFlows,영업에서 창출된 현금흐름,-,제 52 기 반기,18998078000000,,,1,KRW,,제 51 기 반기,8527608000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,당기순이익,-,제 52 기 반기,5828172000000,,,2,KRW,,제 51 기 반기,7151797000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,조정,-,제 52 기 반기,11507434000000,,,3,KRW,,제 51 기 반기,7933853000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,영업활동으로 인한 자산부채의 변동,-,제 52 기 반기,1662472000000,,,4,KRW,,제 51 기 반기,-6558042000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_InterestReceivedClassifiedAsOperatingActivities,이자의 수취,-,제 52 기 반기,252408000000,,,5,KRW,,제 51 기 반기,294659000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_InterestPaidClassifiedAsOperatingActivities,이자의 지급,-,제 52 기 반기,87943000000,,,6,KRW,,제 51 기 반기,159887000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_DividendsReceivedClassifiedAsOperatingActivities,배당금 수입,-,제 52 기 반기,102402000000,,,7,KRW,,제 51 기 반기,1701314000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_IncomeTaxesPaidRefundClassifiedAsOperatingActivities,법인세 납부액,-,제 52 기 반기,1179157000000,,,8,KRW,,제 51 기 반기,8134958000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_CashFlowsFromUsedInInvestingActivities,투자활동 현금흐름,-,제 52 기 반기,-11460790000000,,,9,KRW,,제 51 기 반기,4677057000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,단기금융상품의 순감소(증가),-,제 52 기 반기,2496130000000,,,10,KRW,,제 51 기 반기,14311201000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,기타포괄손익-공정가치금융자산의 처분,-,제 52 기 반기,503000000,,,11,KRW,,제 51 기 반기,271000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,기타포괄손익-공정가치금융자산의 취득,-,제 52 기 반기,0,,,12,KRW,,제 51 기 반기,-6701000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,당기손익-공정가치금융자산의 처분,-,제 52 기 반기,0,,,13,KRW,,제 51 기 반기,268000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,"종속기업, 관계기업 및 공동기업 투자의 처분",-,제 52 기 반기,22058000000,,,14,KRW,,제 51 기 반기,58677000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,"종속기업, 관계기업 및 공동기업 투자의 취득",-,제 52 기 반기,-87761000000,,,15,KRW,,제 51 기 반기,-893077000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_ProceedsFromSalesOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities,유형자산의 처분,-,제 52 기 반기,305261000000,,,16,KRW,,제 51 기 반기,178924000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities,유형자산의 취득,-,제 52 기 반기,13000016000000,,,17,KRW,,제 51 기 반기,7652264000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_ProceedsFromSalesOfIntangibleAssetsClassifiedAsInvestingActivities,무형자산의 처분,-,제 52 기 반기,1054000000,,,18,KRW,,제 51 기 반기,90000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities,무형자산의 취득,-,제 52 기 반기,1237786000000,,,19,KRW,,제 51 기 반기,530064000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,사업결합으로 인한 현금유출액,-,제 52 기 반기,0,,,20,KRW,,제 51 기 반기,-785000000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_OtherInflowsOutflowsOfCashClassifiedAsInvestingActivities,기타투자활동으로 인한 현금유출입액,-,제 52 기 반기,39767000000,,,21,KRW,,제 51 기 반기,-5268000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_CashFlowsFromUsedInFinancingActivities,재무활동 현금흐름,-,제 52 기 반기,-5668416000000,,,22,KRW,,제 51 기 반기,-5904161000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,-표준계정코드 미사용-,단기차입금의 순증가(감소),-,제 52 기 반기,-792923000000,,,23,KRW,,제 51 기 반기,-1036694000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,dart_RepaymentsOfLongTermBorrowings,장기차입금의 상환,-,제 52 기 반기,65766000000,,,24,KRW,,제 51 기 반기,58256000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_DividendsPaidClassifiedAsFinancingActivities,배당금의 지급,-,제 52 기 반기,4809727000000,,,25,KRW,,제 51 기 반기,4809211000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_EffectOfExchangeRateChangesOnCashAndCashEquivalents,외화환산으로 인한 현금의 변동,-,제 52 기 반기,696000000,,,26,KRW,,제 51 기 반기,341000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,ifrs-full_IncreaseDecreaseInCashAndCashEquivalents,현금및현금성자산의 순증감,-,제 52 기 반기,957278000000,,,27,KRW,,제 51 기 반기,1001973000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,dart_CashAndCashEquivalentsAtBeginningOfPeriodCf,기초의 현금및현금성자산,-,제 52 기 반기,2081917000000,,,28,KRW,,제 51 기 반기,2607957000000,
20200814001766,11012,2020,00126380,CF,현금흐름표,dart_CashAndCashEquivalentsAtEndOfPeriodCf,기말의 현금및현금성자산,-,제 52 기 반기,3039195000000,,,29,KRW,,제 51 기 반기,3609930000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_EquityAtBeginningOfPeriod,기초자본,자본 [member]|기타자본항목,제 52 기 반기,280514000000,,,1,KRW,,제 51 기 반기,1131186000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_EquityAtBeginningOfPeriod,기초자본,자본 [member]|주식발행초과금,제 52 기 반기,4403893000000,,,1,KRW,,제 51 기 반기,4403893000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_EquityAtBeginningOfPeriod,기초자본,자본 [member]|자본금 [member],제 52 기 반기,897514000000,,,1,KRW,,제 51 기 반기,897514000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_EquityAtBeginningOfPeriod,기초자본,자본 [member]|이익잉여금 [member],제 52 기 반기,172288326000000,,,1,KRW,,제 51 기 반기,166555532000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_EquityAtBeginningOfPeriod,기초자본,별도재무제표 [member],제 52 기 반기,177870247000000,,,1,KRW,,제 51 기 반기,172988125000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_ProfitLoss,당기순이익(손실),자본 [member]|이익잉여금 [member],제 52 기 반기,5828172000000,,,2,KRW,,제 51 기 반기,7151797000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_ProfitLoss,당기순이익(손실),별도재무제표 [member],제 52 기 반기,3522241000000,,,2,KRW,,제 51 기 반기,4063169000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_ChangesInReserveOfGainsAndLossesOnFinancialAssetsMeasuredAtFairValueThroughOtherComprehensiveIncome,기타포괄손익-공정가치금융자산평가손익,자본 [member]|기타자본항목,제 52 기 반기,-101373000000,,,3,KRW,,제 51 기 반기,99627000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,dart_ChangesInReserveOfGainsAndLossesOnFinancialAssetsMeasuredAtFairValueThroughOtherComprehensiveIncome,기타포괄손익-공정가치금융자산평가손익,별도재무제표 [member],제 52 기 반기,-101373000000,,,3,KRW,,제 51 기 반기,99627000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,-표준계정코드 미사용-,순확정급여자산 재측정요소,자본 [member]|기타자본항목,제 52 기 반기,-36568000000,,,4,KRW,,제 51 기 반기,-40739000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,-표준계정코드 미사용-,순확정급여자산 재측정요소,별도재무제표 [member],제 52 기 반기,-36568000000,,,4,KRW,,제 51 기 반기,-40739000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_DividendsPaid,배당,별도재무제표 [member],제 52 기 반기,4810033000000,,,5,KRW,,제 51 기 반기,4810032000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_DividendsPaid,배당,자본 [member]|이익잉여금 [member],제 52 기 반기,4810033000000,,,5,KRW,,제 51 기 반기,4810032000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_Equity,기말자본,자본 [member]|이익잉여금 [member],제 52 기 반기,173306465000000,,,6,KRW,,제 51 기 반기,168897297000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_Equity,기말자본,자본 [member]|자본금 [member],제 52 기 반기,897514000000,,,6,KRW,,제 51 기 반기,897514000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_Equity,기말자본,자본 [member]|기타자본항목,제 52 기 반기,142573000000,,,6,KRW,,제 51 기 반기,1190074000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_Equity,기말자본,자본 [member]|주식발행초과금,제 52 기 반기,4403893000000,,,6,KRW,,제 51 기 반기,4403893000000,
20200814001766,11012,2020,00126380,SCE,자본변동표,ifrs-full_Equity,기말자본,별도재무제표 [member],제 52 기 반기,178750445000000,,,6,KRW,,제 51 기 반기,175388778000000,
```
##### sample code snippet
```python
import os, csv, glob
import pandas as pd
import numpy as np
import argparse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError
import logging

Base = declarative_base()

log_file_path = "./insert_finance.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

class CorpInfo(Base):
    __tablename__ = "corp_info"
    corp_code = Column(String(8), primary_key=True)
    corp_name = Column(String)
    corp_name_eng = Column(String)
    stock_name = Column(String)
    stock_code = Column(String)
    ceo_nm = Column(String)
    corp_cls = Column(String)
    jurir_no = Column(String)
    bizr_no = Column(String)
    adres = Column(String)
    hm_url = Column(String)
    ir_url = Column(String)
    phn_no = Column(String)
    fax_no = Column(String)
    induty_code = Column(String)
    est_dt = Column(String)
    acc_mt = Column(String)
    logo_img_url = Column(String)


class FinancialReportBase(Base):
    __tablename__ = "financial_report_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rcept_no = Column(String(14))
    reprt_code = Column(String(5), nullable=False)
    bsns_year = Column(String(4), nullable=False)
    corp_code = Column(String(8), ForeignKey("corp_info.corp_code"), nullable=False)
    report_type = Column(String(1), nullable=False)
    fs_type = Column(String(3), nullable=False)


class FinancialStatement(Base):
    __tablename__ = "financial_statement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("financial_report_base.id"))
    sj_div = Column(String(3), nullable=False)
    sj_nm = Column(String)
    account_id = Column(String(3), nullable=False)
    account_nm = Column(String)
    account_detail = Column(String)
    thstrm_nm = Column(String)
    thstrm_amount = Column(BigInteger)
    frmtrm_nm = Column(String(255))
    frmtrm_amount = Column(BigInteger)
    ord = Column(Integer)
    currency = Column(String(3))


class FinancialQuarterlyReport(Base):
    __tablename__ = "financial_quarterly_report"
    id = Column(Integer, ForeignKey("financial_statement.id"), primary_key=True)
    frmtrm_q_nm = Column(String)
    frmtrm_q_amount = Column(BigInteger)
    frmtrm_add_amount = Column(BigInteger)
    thstrm_add_amount = Column(BigInteger)


class FinancialAnnualReport(Base):
    __tablename__ = "financial_annual_report"
    id = Column(Integer, ForeignKey("financial_statement.id"), primary_key=True)
    bfefrmtrm_nm = Column(String)
    bfefrmtrm_amount = Column(BigInteger)


def main():
    parser = argparse.ArgumentParser(description="Read CSV and save to DB")
    parser.add_argument(
        "--corp_list", required=True, help="Path to the corp_code list file"
    )
    args = parser.parse_args()

    # DB setup
    engine = create_engine(
        "postgresql+psycopg2://skopenai:!skcc1234@infratf-db.postgres.database.azure.com:5432/chatbot?sslmode=allow"
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Read corp codes
    with open(args.corp_list, "r", newline="", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            corp_code = row["corp_code"]
            logging.info(
                "======================================================================="
            )
            logging.info("Start new company!!!")
            logging.info(f"corp_code: {corp_code}")

            for year in range(2020, 2024):
                logging.info(f"year: {year}")
                file_pattern = f"./finance_download/{corp_code}_{year}_*.csv"

                for filename in glob.glob(file_pattern):
                    logging.info(
                        "-----------------------------------------------------------------------"
                    )
                    logging.info(f"file to process: {filename}")
                    df = pd.read_csv(filename)

                    # preprocess data
                    # Your list of columns to convert
                    cols_to_convert = [
                        "thstrm_amount",
                        "frmtrm_amount",
                        "frmtrm_q_amount",
                        "frmtrm_add_amount",
                        "bfefrmtrm_amount",
                        "thstrm_add_amount",
                    ]

                    # Create a dictionary for columns that need to be converted to Int64
                    existing_cols = {
                        col: "Int64" for col in cols_to_convert if col in df.columns
                    }

                    # Fill NaN values and convert types in one go
                    for col in existing_cols.keys():
                        df[col] = df[col].fillna(0).astype(np.int64)

                    df["rcept_no"] = df["rcept_no"].astype(str)
                    df["reprt_code"] = df["reprt_code"].astype(str)
                    df["bsns_year"] = df["bsns_year"].astype(str)
                    df["corp_code"] = df["corp_code"].astype(str)

                    # Replace NaN with None
                    df.replace({pd.NaT: None, pd.NA: None, np.nan: None}, inplace=True)

                    # Prepare a list to hold the rows to be inserted in batch
                    financial_statement_list = []
                    financial_annual_report_list = []
                    financial_quarterly_report_list = []

                    reprt_code = df["reprt_code"].iloc[0]

                    try:
                        # Step 1: Save to financial_report_base
                        financial_report_base = FinancialReportBase(
                            rcept_no=df["rcept_no"].iloc[0],
                            reprt_code=reprt_code,
                            bsns_year=df["bsns_year"].iloc[0],
                            corp_code=corp_code,
                            report_type="A" if reprt_code == "11011" else "Q",
                            fs_type="OFS",
                        )
                        session.add(financial_report_base)
                        session.commit()
                        logging.info("financial_report_base commit ok")

                        # Step 2: Save to financial_statement
                        for _, row in df.iterrows():
                            financial_statement_dict = {
                                "report_id": financial_report_base.id,
                                "sj_div": row["sj_div"],
                                "sj_nm": row["sj_nm"],
                                "account_id": row["account_id"],
                                "account_nm": row["account_nm"],
                                "thstrm_nm": row["thstrm_nm"],
                                "thstrm_amount": int(row["thstrm_amount"]),
                                "frmtrm_nm": row["frmtrm_nm"],
                                "frmtrm_amount": int(row["frmtrm_amount"]),
                                "ord": row["ord"],
                                "currency": row["currency"],
                            }
                            financial_statement_list.append(financial_statement_dict)

                        # Batch insert and commit for financial_statement
                        session.bulk_insert_mappings(
                            FinancialStatement, financial_statement_list
                        )
                        session.commit()
                        logging.info("financial_statement commit ok")

                        # Query last inserted set of IDs
                        last_ids = (
                            session.query(FinancialStatement.id)
                            .order_by(FinancialStatement.id.desc())
                            .limit(len(financial_statement_list))
                            .all()
                        )
                        last_ids = [i[0] for i in reversed(last_ids)]

                        # Step 3: Prepare data for financial_annual_report and financial_quarterly_report
                        financial_annual_report_list = []
                        financial_quarterly_report_list = []

                        for idx, (_, row) in enumerate(df.iterrows()):
                            id_reference = last_ids[idx]

                            if reprt_code == "11011":
                                financial_annual_report_dict = {
                                    "id": id_reference,
                                    "bfefrmtrm_nm": row["bfefrmtrm_nm"],
                                    "bfefrmtrm_amount": int(row["bfefrmtrm_amount"]),
                                }
                                financial_annual_report_list.append(
                                    financial_annual_report_dict
                                )
                            else:
                                financial_quarterly_report_dict = {
                                    "id": id_reference,
                                    "frmtrm_q_nm": row["frmtrm_q_nm"],
                                    "frmtrm_q_amount": int(row["frmtrm_q_amount"]),
                                    "frmtrm_add_amount": int(row["frmtrm_add_amount"]),
                                    "thstrm_add_amount": int(row["thstrm_add_amount"]),
                                }
                                financial_quarterly_report_list.append(
                                    financial_quarterly_report_dict
                                )

                        # Batch insert
                        session.bulk_insert_mappings(
                            FinancialAnnualReport, financial_annual_report_list
                        )
                        session.bulk_insert_mappings(
                            FinancialQuarterlyReport,
                            financial_quarterly_report_list,
                        )

                        # Commit transaction
                        session.commit()
                        logging.info(
                            f"Saved data for corp_code: {corp_code}, year: {year}"
                        )
                    except IntegrityError:
                        session.rollback()
                        logging.error(
                            f"IntegrityError: A unique constraint or foreign key constraint violation occurred for corp_code: {corp_code}, year: {year}"
                        )
                    except StatementError:
                        session.rollback()
                        logging.error(
                            f"StatementError: Invalid SQL expression or a bad parameter for corp_code: {corp_code}, year: {year}"
                        )
                    except SQLAlchemyError as e:
                        session.rollback()
                        logging.error(
                            f"SQLAlchemyError: An unknown SQLAlchemy error occurred for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )
                    except Exception as e:
                        session.rollback()
                        logging.error(
                            f"An unknown error occurred for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )


if __name__ == "__main__":
    main()
```

## 데이터프레임의 각 레코드마다 어떤 작업을 하려고 할 때
### dataframe.iterrows()
- generator function
- returns tuple (index, Series)
- sample code
```python
import pandas as pd

# Create a simple DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Occupation': ['Engineer', 'Doctor', 'Artist']
})

# Iterating over rows using iterrows
for index, row in df.iterrows():
    print(f"Index: {index}")
    print(f"Name: {row['Name']}")
    print(f"Age: {row['Age']}")
    print(f"Occupation: {row['Occupation']}")
    print("----")
```
- output
```python
Index: 0
Name: Alice
Age: 25
Occupation: Engineer
----
Index: 1
Name: Bob
Age: 30
Occupation: Doctor
----
Index: 2
Name: Charlie
Age: 35
Occupation: Artist
----
```

#### iterrows()로 데이터 프레임 각 레코드를 DB에 저장
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import argparse


def save_csv_to_db(input_csv):
    # Connect to the PostgreSQL database
    engine = create_engine(
        "postgresql+psycopg2://skopenai:!skcc1234@infratf-db.postgres.database.azure.com:5432/chatbot?sslmode=allow"
    )

    # Create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Loop through the DataFrame and add each row to the database
    for index, row in df.iterrows():
        # Your table class definition might differ. Make sure to match it accordingly.
        corp_info_instance = CorpInfo(
            corp_code=row["corp_code"],
            corp_name=row["corp_name"],
            corp_name_eng=row["corp_name_eng"],
            stock_name=row["stock_name"],
            stock_code=row["stock_code"],
            ceo_nm=row["ceo_nm"],
            corp_cls=row["corp_cls"],
            jurir_no=row["jurir_no"],
            bizr_no=row["bizr_no"],
            adres=row["adres"],
            hm_url=row["hm_url"],
            ir_url=row["ir_url"],
            phn_no=row["phn_no"],
            fax_no=row["fax_no"],
            induty_code=row["induty_code"],
            est_dt=row["est_dt"],
            acc_mt=row["acc_mt"],
            # logo_img_url=row['logo_img_url']  # Assuming this field is not in your CSV
        )

        session.add(corp_info_instance)

    # Commit the changes
    session.commit()


# Define your SQLAlchemy CorpInfo class to mirror the database table structure.
Base = declarative_base()


class CorpInfo(Base):
    __tablename__ = "corp_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(8))
    corp_name = Column(String)
    corp_name_eng = Column(String)
    stock_name = Column(String)
    stock_code = Column(String(6))
    ceo_nm = Column(String(50))
    corp_cls = Column(String(1))
    jurir_no = Column(String(13))
    bizr_no = Column(String(10))
    adres = Column(String)
    hm_url = Column(String)
    ir_url = Column(String)
    phn_no = Column(String(25))
    fax_no = Column(String(25))
    induty_code = Column(String(10))
    est_dt = Column(String(8))
    acc_mt = Column(String(2))
    logo_img_url = Column(String)  # Assuming this field is not in your CSV


parser = argparse.ArgumentParser(description="Save CSV to Database.")
parser.add_argument("input_csv", help="Path to the input CSV file.")

# Run the function
if __name__ == "__main__":
    args = parser.parse_args()
    save_csv_to_db(args.input_csv)
```

### loc
칼럼 중 하나를 set_index로 했을 때 해당 칼럼의 값으로 추출
### iloc
- set_index()를 하지 않았거나 상관없이 그냥 순수한 index값으로만 추출할 때
- iloc.ipynb
```python
import pandas as pd

# Initializing the nested list with Data set
player_list = [['M.S.Dhoni', 36, 75, 5428000],
               ['A.B.D Villers', 38, 74, 3428000],
               ['V.Kohli', 31, 70, 8428000],
               ['S.Smith', 34, 80, 4428000],
               ['C.Gayle', 40, 100, 4528000],
               ['J.Root', 33, 72, 7028000],
               ['K.Peterson', 42, 85, 2528000]]

# creating a pandas dataframe
df = pd.DataFrame(player_list, columns=['Name', 'Age', 'Weight', 'Salary'])
print(df)
print('--------------------------------')

# Slicing rows in data frame
df1 = df.iloc[0:4]
print(df1)
print('--------------------------------')

# Slicing columnss in data frame
df2 = df.iloc[:, 0:2]
print(df2)
print('--------------------------------')

# Select a cell
cell = df.iloc[2, 3]
print(cell)
print('--------------------------------')
```
- output
```shell
Name  Age  Weight   Salary
0      M.S.Dhoni   36      75  5428000
1  A.B.D Villers   38      74  3428000
2        V.Kohli   31      70  8428000
3        S.Smith   34      80  4428000
4        C.Gayle   40     100  4528000
5         J.Root   33      72  7028000
6     K.Peterson   42      85  2528000
--------------------------------
            Name  Age  Weight   Salary
0      M.S.Dhoni   36      75  5428000
1  A.B.D Villers   38      74  3428000
2        V.Kohli   31      70  8428000
3        S.Smith   34      80  4428000
--------------------------------
            Name  Age
0      M.S.Dhoni   36
1  A.B.D Villers   38
2        V.Kohli   31
3        S.Smith   34
4        C.Gayle   40
5         J.Root   33
6     K.Peterson   42
--------------------------------
8428000
--------------------------------
```
