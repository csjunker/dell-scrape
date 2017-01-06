import pandas as pd
from lxml import html

url = r'http://downloads.dell.com/published/pages/latitude-e5540-laptop.html'
from IPython.display import display, HTML


#xpath = "//*[@id=\"Drivers-Category.BI\"]/table[1]"
#xpath = "//*[@id=\"Drivers-Category.BI-Type.BIOS\"]/table[1]"
xpath = "//table//table"

tree = html.parse(url)

tables = tree.xpath(xpath)

#table = tables[0]
#raw_html = html.tostring(table)
#data = pd.read_html(raw_html, header=0)
#print("len", len(data))
#data[0].to_string()
#data[0]
#print ("<html><body>")

for table in tables:
    raw_html = html.tostring(table)
    data = pd.read_html(raw_html, header=0)
    #print("len", len(data))
    #data[0]
    #print(data[0].to_html())
    #display(data[0])
    #print(data[0]['Release'])
    for x in data[0].iterrows():
        print (x)
