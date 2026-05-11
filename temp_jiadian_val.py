# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".opencode/skills"))

import akshare as ak
import time

print('=== Trying 行业估值 ===')
try:
    df = ak.stock_industry_pe_ratio_cninfo()
    print('Data columns:', df.columns.tolist())
    print('Total rows:', len(df))
    print()
    
    # Find 家电
    for idx, row in df.iterrows():
        name = str(row.iloc[0])
        if '家电' in name:
            print('Found: ' + name)
            print('  PE: ' + str(row.iloc[3]))
            print('  PE median: ' + str(row.iloc[4]))
            print('  PB: ' + str(row.iloc[5]))
            print('  PB median: ' + str(row.iloc[6]))
            break
    else:
        print('All industries with "家" or "电":')
        for idx, row in df.iterrows():
            name = str(row.iloc[0])
            if '家' in name or '电' in name:
                print('  ' + name + ' PE=' + str(row.iloc[3]))
except Exception as e:
    print('Error: ' + str(e))
    
print()
print('=== Trying 成分股 ===')
try:
    time.sleep(2)
    df = ak.stock_board_industry_cons_em(symbol='家电行业')
    print('Found %d stocks' % len(df))
    if not df.empty:
        print(df.head())
except Exception as e:
    print('Error: ' + str(e))