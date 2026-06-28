import socket,ssl,re,base64,concurrent.futures,urllib.request
from datetime import datetime,timezone

SOURCES=["https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt","https://raw.githack.com/igareck/vpn-configs-for-russia/main/Black-Lists-Tops-150.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/6.1.txt","https://gitlab.com/igareck/vpn-configs-for-russia/-/raw/main/Vless-Reality-White-Lists-Rus-Mobile.txt"]
PROTO=("vless://","vmess://","trojan://","ss://","hy2://","hysteria2://","tuic://")

def fetch(url):
  try:
    r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=15)
    return r.read().decode("utf-8","ignore")
  except:return ""

def parse(c):
  m=re.search(r'@([^@\s\[\]]+):(\d+)',c)
  if m:return m.group(1),int(m.group(2))
  return None,None

def check(c):
  import time
  h,p=parse(c)
  if not h:return None,9999
  try:
    s=socket.create_connection((h,p),timeout=3)
    s.close()
  except:return None,9999
  try:
    ctx=ssl.create_default_context()
    ctx.check_hostname=False
    ctx.verify_mode=ssl.CERT_NONE
    t0=time.time()
    conn=ctx.wrap_socket(socket.socket(),server_hostname=h)
    conn.settimeout(4)
    conn.connect((h,p))
    lat=int((time.time()-t0)*1000)
    conn.close()
    return c,lat
  except:pass
  try:
    t0=time.time()
    s=socket.create_connection((h,p),timeout=3)
    lat=int((time.time()-t0)*1000)
    s.close()
    if lat<300:return c,lat
  except:pass
  return None,9999

all_c=set()
for u in SOURCES:
  t=fetch(u)
  found=[l.strip() for l in t.splitlines() if any(l.strip().startswith(p) for p in PROTO)]
  all_c.update(found)
  print(f"  {u.split('/')[-1]}: {len(found)}")

print(f"Всего: {len(all_c)}")

working=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
  futs={ex.submit(check,c):c for c in all_c}
  done=0
  for f in concurrent.futures.as_completed(futs):
    done+=1
    r,lat=f.result()
    if r:working.append((lat,r))
    if done%50==0:print(f"  {done}/{len(all_c)}, рабочих: {len(working)}")

working.sort(key=lambda x:x[0])
good=[c for lat,c in working if lat<300]
print(f"Рабочих <300мс: {len(good)}")

now=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
if good:
  open("sub.txt","w").write(base64.b64encode("\n".join(good).encode()).decode())
  open("sub_plain.txt","w").write(f"# Lejopka | {now} | {len(good)} серверов\n"+"\n".join(good))
  open("README.md","w").write(f"# Lejopka VPN\n\nПодписка:\n```\nhttps://raw.githack.com/lejopka/lejopka/main/sub.txt\n```\n**Серверов <300мс:** {len(good)}\n**Обновлено:** {now}\n\n## Как добавить\nHapp → **+** → **URL подписки** → вставь\n")
  print("Готово!")
else:
  print("Рабочих нет!")
