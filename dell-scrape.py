import pandas as pd
from lxml import html
from IPython.display import display

import laptop_list
#laptops = {'Latitude E5570': '1.11.4', 'Precision 7510': '1.9.5', 'Latitude E6540': 'A16'}
laptops = laptop_list.laptops



base_url = r'http://downloads.dell.com/published/pages/'
search_url = base_url + 'index.html'
xpath = "//*[@id=\"Drivers-Category.BI-Type.BIOS\"]/table[1]"


oversigt = html.parse(search_url)

for laptop in laptops:
    url = base_url + oversigt.xpath("//a[text()='" + laptop + "']/@href")[0]
    print(laptop, url)
    tree = html.parse(url)
    table = tree.xpath(xpath)[0]
    raw_html = html.tostring(table)
    data = pd.read_html(raw_html, header=0)[0]
    #del data["Download"]
    row = data.iloc[0]
    print('Released', row['Released'])
    print('Version', row['Version'])
    print('Importance', row['Importance'])
    print('Download', row['Download'])
    display(data.head(4))
    print()
