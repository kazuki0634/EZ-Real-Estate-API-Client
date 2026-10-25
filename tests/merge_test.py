import pandas as pd

df_ab = pd.DataFrame({'a': ['a_1', 'a_2', 'a_3'], 'b': ['b_1', 'b_2', 'b_3']})
df_ac = pd.DataFrame({'a': ['a_1', 'a_2', 'a_4'], 'b': ['c_1', 'c_2', 'c_4']})


print(df_ab)

print(df_ac)

print(pd.concat([df_ab, df_ac]))
