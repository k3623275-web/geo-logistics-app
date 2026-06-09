with open(r'C:\工作场地\geo-logistics-app\index.html', 'r', encoding='utf-8-sig') as f:
    d = f.read()

# Find pageAI section
idx = d.find('id="pageAI"')
if idx < 0:
    idx = d.find("id='pageAI'")
print('pageAI at:', idx)

# Find ai-page.js content
with open(r'C:\工作场地\geo-logistics-app\ai-page.js', 'r', encoding='utf-8-sig') as f:
    js = f.read()
print('ai-page.js: %d chars' % len(js))
print('First 3000 chars of ai-page.js:')
print(js[:3000])
