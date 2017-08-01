import pandas as pd

from lxml import html

#from IPython.display import display

base_url = r'http://downloads.dell.com/published/pages/'
search_url = base_url + 'index.html'
xpath = "//*[@id=\"Drivers-Category.BI-Type.BIOS\"]/table[1]"

laptops = ['Latitude E5570', 'Precision 7510', 'Latitude E6540']

oversigt = html.parse(search_url)


def  fetchLaptopData(laptop):
    url = base_url + oversigt.xpath("//a[text()='" + laptop + "']/@href")[0]
    print(laptop, url)
    tree = html.parse(url)
    table = tree.xpath(xpath)[0]
    raw_html = html.tostring(table)
    return  pd.read_html(raw_html, header=0)[0]

def beginLaptop(fp, laptop):
    fp.write('<div id="')
    fp.write(laptop)
    fp.write('" class="laptop">\n')
    fp.write('<h3>')
    fp.write(laptop)
    fp.write('</h3>\n')

def makeRow(fp, clst, row):
    fp.write('<tr>')
    ser = row[1]
    for key in clst:
        fp.write('   <td>')
        fp.write(str(ser[key]))
        fp.write('</td>\n')
    fp.write('<tr>\n')

def makeTable(fp, data):
    clst = list(data)
    fp.write('<table class="laptop-table">\n')
    fp.write('<thead><tr>')
    #print('###')
    for key in clst:
        #print('#', key)
        fp.write('<th>')
        fp.write(key)
        fp.write('</th>')
    #print('#####')
    fp.write('</thead>\n')
    fp.write('<tbody>\n')
    for row in data.iterrows():
        makeRow(fp, clst, row)
    fp.write('</tbody></table>\n')

with open('dell-bios.html', 'w') as fp:
    fp.write('<!DOCTYPE html>\n<html><head><title>Dell Bios</title></head>\n')
    fp.write('<body><h2>Dell Bios</h2>\n')

    for laptop in laptops:
        print(laptop)
        fp.write('<div id="')
        fp.write(laptop)
        fp.write('" class="laptop">\n')
        fp.write('<h3>')
        fp.write(laptop)
        fp.write('</h3>')
        data = fetchLaptopData(laptop)
        #clst = list(data)
        makeTable(fp, data)
        fp.write('</div>\n')

    fp.write('</body></html>')


