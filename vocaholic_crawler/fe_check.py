#!/usr/bin/env python
# coding: utf-8

# In[39]:


from bs4 import BeautifulSoup
import time
from selenium import webdriver
import requests
import lxml.html as lh
import pandas as pd
from distutils.version import LooseVersion
url = "http://aac-srvtts-tools.nuance.com/vocaholic/fe/release/?language=czc"


# In[40]:


browser = webdriver.Chrome()

browser.get(url)
#time.sleep(3)
html = browser.page_source
soup = BeautifulSoup(html, "lxml")

#print(len(soup.find_all("table")))
table=soup.find("table", {"id": "myTable"})
#print(table)

browser.close()
browser.quit()


# In[41]:


table_rows = table.find_all('tr')
rows=[]
for tr in table_rows:
    td = tr.find_all('td')
    row = [tr.text for tr in td]
    rows.append(row)

#print(df)


# In[42]:


cols=soup.find_all("th")
col_names=[]
for th in cols:
    col=th.text
    col_names.append(col)
#print(col_names[:16])
#print(len(col_names[:16]))
cols = col_names[:17]

#cols=info_tr.findall('th')
#print(cols)


# In[45]:


print(cols)


# In[43]:


df=pd.DataFrame(rows,columns=cols)
df.to_csv('FE_check.csv',sep=';' ,index=False,encoding='utf-8_sig')


# In[50]:


print(df[[  'Voice', 'FE_CFG', 'FE_Voice Version', 'CLC Version', 'VLC Version', 'Published Date', 'Used In']].head())


# In[ ]:




