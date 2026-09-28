import re
x = open('/tmp/mouseext_ss.xml').read()   # superseries GSM lists
s = open('/tmp/subs.xml').read()          # subseries GSM lists

def gsms(doc):
    out = {}
    acc = re.search(r'<Item Name="Accession" Type="String">(GSE\d+)', doc)
    for m in re.finditer(r'<Item Name="Accession" Type="String">(GSM\d+)</Item>\s*<Item Name="Title" Type="String">(.*?)</Item>', doc):
        out[m.group(1)] = m.group(2)
    return (acc.group(1) if acc else '?'), out

sup = {}
for d in x.split('<DocSum>')[1:]:
    a, g = gsms(d)
    sup[a] = g
sub = {}
for d in s.split('<DocSum>')[1:]:
    a, g = gsms(d)
    sub[a] = g

for sa in ('GSE133382', 'GSE81904'):
    pa = 'GSE137400' if sa == 'GSE133382' else 'GSE81905'
    inter = set(sub[sa]) & set(sup[pa])
    print('%s: %d GSM ; parent %s: %d GSM ; GSM overlap: %d' % (sa, len(sub[sa]), pa, len(sup[pa]), len(inter)))
    for g in sorted(sub[sa]):
        print('    ', g, '|', sub[sa][g][:60], '| in_parent:', g in inter)
