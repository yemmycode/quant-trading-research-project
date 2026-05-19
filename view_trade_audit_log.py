
"""
View latest trade audit log records.
"""

from trade_audit import read_audit_log


def main():
    df = read_audit_log(limit=50)

    if df.empty:
        print("No trade audit log records found.")
    else:
        print("Latest Trade Audit Log Records")
        print("==============================")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
