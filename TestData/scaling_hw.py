# -*- coding: utf-8 -*-
"""
Pandas aggregation with grouping lab

@author: Glenn Bruns
"""
import pandas as pd

# allow output to span multiple output lines in the console
pd.set_option('display.max_columns', 500)

# =============================================================================
# Read the data
#
# This is data from the 1994 US census.
# You can treat it as if each row of the data set represents one person.
# Variables in the data set include age, education, native country, and
# whether income is > $50K.
#
# =============================================================================

df = pd.read_csv("https://raw.githubusercontent.com/grbruns/cst383/master/1994-census-summary.csv")
# drop unused columns
drop_cols = ['usid', 'fnlwgt', 'marital_status', 'relationship', 'race', 'sex', 
             'capital_gain', 'capital_loss', 'label']
df.drop(drop_cols, axis=1, inplace=True)

# =============================================================================
# Basic data exploration
# =============================================================================

# 0
# use df.info() to see the columns of the dataframe
df.info()
# =============================================================================
# Aggregation with value_counts()
# =============================================================================

# 1
# Write an expression to get the number of people in each category of
# 'education'.
print(df['education'].value_counts())
# 2
# write an expression to get the number of people in each category of 
# 'workclass'
print(df['workclass'].value_counts())
# =============================================================================
# Aggregation with groupby()
# =============================================================================

# 3
# For each native country, what is the average education num?
# (use variable 'education_num')
print(df.groupby('native_country')['education_num'].mean())
# 4
# Repeat the previous problem, sorting the output by the average
# education num value.

# 5
# For each occupation, compute the average age

# 6
# Find average hours_per_week for those with age <= 40, and those with age > 40
# (use a condition, not a column of the dataframe, in the groupby).

# 7
# Do the same, but for age groups < 40, 40-60, and > 60.

# =============================================================================
# Vectorized string operations
# =============================================================================

# 8
# Create a Pandas series containing the values in the native_country column.
# Name this series 'country'.

# 9
# How many different values appear in the country series?
# Hint: you can use the Series methods .unique() or .nunique() to solve this.

# 10
# Create a *pandas series* containing the unique country names in the series.
# Name this new series 'country_names'.

# 11
# Modify country_names so that underscore '_' is replaced
# by a hyphen '-' in every country name.  Use a Pandas string operation.
# (Pandas string operations are documented at
# https://pandas.pydata.org/pandas-docs/stable/user_guide/text.html)
# Hint: look into the replace() method.

# 12
# Modify country_names to replace 'Holand' with 'Holland'.

# 13
# Modify country_names so that any characters after 5 are removed.
# Again, use a vectorized operation