# created by: Ethan PP Cutting (100942775)
# created date: 7/10/24
# last modified by: Ethan PP Cutting 
# modified date: 7/10/24

import pandas as pd
import numpy as np

# scale data
def scale_data(column):
    return (column - column.min()) / (column.max() - column.min())

# risk scoring algorithm 
def calculcate_risk_scores(df):
    # weight for each factor
    CVE_WEIGHT = 0.5
    CWE_WEIGHT = 0.3
    TTP_WEIGHT = 0.2

    # scale each factor
    df['scal_cve'] = Scale(df['CVE Severity'])
    df['scal_cve'] = Scale(df['CVE Severity'])
    df['scal_cve'] = Scale(df['CVE Severity'])

    # apply weight
    df['weighted_cve'] = (df['scal_cve']) * CVE_WEIGHT
    df['weighted_cwe'] = (df['scal_cwe']) * CWE_WEIGHT
    df['weighted_ttp'] = (df['scal_ttp']) * TTP_WEIGHT

    # calculate overwall risk score
    df ['risk_score'] = df['weighted_cve'] + df['weighted_cwe'] + df['weighted_ttp']
    return df[['name', 'risk_score']]

    # example usage
data = {
        'name': ['APT28', 'APT37', 'APT38'],
        'CVE Severity': [9.8, 7.5, 5.0],
        'CWE Impact': [3, 2, 1],
        'TTP Frequency': [12, 8, 5]
    }
      
df = pd.DataFrame(data)
risk_scores = calculcate_risk_scores(df)
print(risk_scores)

