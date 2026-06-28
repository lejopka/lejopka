import base64,socket,urllib.request,concurrent.futures,re,subprocess,sys
from datetime import datetime

SOURCES=["https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt","https://raw.githack.com/igareck/vpn-configs-for-russia/main/Black-Lists-Tops-150.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/6.1.txt","https://gitlab.com/igareck/vpn-configs-for-russia/-/raw/main/Vless-Reality-White-Lists-Rus-Mobile.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/22.1.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/24.1.txt"]
PROTO=("vless://","vmess://","trojan://","ss://","hy2://","hysteria2://","tuic://")

def fetch(url):
  try:
    r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=15)
    return r.read().decode("utf-8","ignore")
  except:
    return ""

def parse(c):
  m=re.search(r'@([^@\s\[\]]+):(\d+)',c)
  if m:return m.group(1),int(m.group(2))
  m=re.search(r'@\[([^\]]+)\]:(\d+)',c)
  if m:return m.group(1),int(m.group(2))
  return None,None

def check(c):
  c=c.strip()
  if not c or not any(c.startswith(p) for p in PROTO):return None
  h,p=parse(c)
  if not h or not p:return None
  # Проверяем TCP соединение дважды для надёжности
  for timeout in [3,5]:
    try:
      with socket.create_connection((h,p),timeout=timeout):return c
    except:pass
  return None

# Скачиваем
all_c=set()
for u in SOURCES:
  t=fetch(u)
  lines=[l.strip() for l in t.splitlines() if any(l.strip().startswith(p) for p in PROTO)]
  all_c.update(lines)
  print(f"  {u.split('/')[-1]}: {len(lines)} конфигов")

print(f"Всего: {len(all_c)}")

# Проверяем параллельно
working=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
  futs={ex.submit(check,c):c for c in all_c}
  done=0
