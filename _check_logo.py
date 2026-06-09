with open(r'C:\工作场地\geo-logistics-app\index.html','r',encoding='utf-8-sig') as f:
    d = f.read()

# Find logo-hex HTML
idx = d.find('<div class="logo-hex">')
print('logo-hex HTML at:', idx)
if idx >= 0:
    print('Logo HTML:')
    print(d[idx:idx+350])
