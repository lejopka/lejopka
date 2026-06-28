import base64,socket,urllib.request,concurrent.futures,re
from datetime import datetime

SOURCES=["https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt","https://raw.githack.com/igareck/vpn-configs-for-russia/main/Black-Lists-Tops-150.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/6.1.txt","https://gitlab.com/igareck/vpn-configs-for-russia/-/raw/main/Vless-Reality-White-Lists-Rus-Mobile.txt"]
PROTO=("vless://","vmess://","trojan://","ss://","hy2://","hysteria2://","tuic://")

def fetch(url):
  try:
    r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=15)
    t=r.read().decode("utf-8","ignore")
    return t
  except:
    return ""

def parse(c):
  m=re.search(r'@([^@\s]+):(\d+)',c)
  return (m.group(1),int(m.group(2))) if m else (None,None)

def check(c):
  c=c.strip()
  if not c or not any(c.startswith(p) for p in PROTO):return None
  h,p=parse(c)
  if not h:return None
  try:
    with socket.create_connection((h,p),timeout=4):return c
  except:return None

all_c=set()
for u in SOURCES:
  t=fetch(u)
  all_c.update(l.strip() for l in t.splitlines() if any(l.strip().startswith(p) for p in PROTO))

working=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
  for r in concurrent.futures.as_completed([ex.submit(check,c) for c in all_c]):
    if r.result():working.append(r.result())

if working:
  open("sub.txt","w").write(base64.b64encode("\n".join(working).encode()).decode())
  open("sub_plain.txt","w").write(f"# Lejopka {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | Серверов: {len(working)}\n"+"\n".join(working))
  open("README.md","w").write(f"# Lejopka VPN\n\nПодписка для Happ:\n```\nhttps://raw.githack.com/lejopka/lejopka/main/sub.txt\n```\nРабочих серверов: {len(working)}\nОбновлено: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
print(f"Done: {len(working)} servers")
