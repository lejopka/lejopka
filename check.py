import base64,socket,urllib.request,concurrent.futures,re,subprocess,os
from datetime import datetime

SOURCES=["https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt","https://raw.githack.com/igareck/vpn-configs-for-russia/main/Black-Lists-Tops-150.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/1.1.txt","https://raw.githack.com/Hidashimora/free-vpn-anti-rkn/main/configs/6.1.txt","https://gitlab.com/igareck/vpn-configs-for-russia/-/raw/main/Vless-Reality-White-Lists-Rus-Mobile.txt"]
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

def check_tcp(h,p):
  for t in [2,4]:
    try:
      with socket.create_connection((h,p),timeout=t):return True
    except:pass
  return False

def check_http(h,p):
  # Дополнительно проверяем через HTTP запрос на популярные сайты через прокси
  try:
    import urllib.request
    proxy=urllib.request.ProxyHandler({'http':f'http://{h}:{p}','https':f'http://{h}:{p}'})
    opener=urllib.request.build_opener(proxy)
    opener.open("http://www.gstatic.com/generate_204",timeout=5)
    return True
  except:
    return False

def check(c):
  c=c.strip()
  if not c or not any(c.startswith(p) for p in PROTO):return None
  h,p=parse(c)
  if not h or not p:return None
  if check_tcp(h,p):return c
  return None

# Скачиваем
all_c=set()
for u in SOURCES:
  t=fetch(u)
  lines=[l.strip() for l in t.splitlines() if any(l.strip().startswith(p) for p in PROTO)]
  all_c.update(lines)
  print(f"  {u.split('/')[-1]}: {len(lines)}")

print(f"Всего уникальных: {len(all_c)}")

# Проверяем
working=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=200) as ex:
  futs={ex.submit(check,c):c for c in all_c}
  done=0
  for f in concurrent.futures.as_completed(futs):
    done+=1
    r=f.result()
    if r:working.append(r)
    if done%100==0:print(f"  {done}/{len(all_c)}, рабочих: {len(working)}")

print(f"Итого рабочих: {len(working)}")

# Берём источник igareck отдельно — он уже проверен автором
bonus=fetch("https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt")
bonus_lines=[l.strip() for l in bonus.splitlines() if any(l.strip().startswith(p) for p in PROTO)]
# Объединяем рабочие + проверенные от igareck
final=list(set(working+bonus_lines))
print(f"Финальный список: {len(final)} серверов")

if final:
  open("sub.txt","w").write(base64.b64encode("\n".join(final).encode()).decode())
  open("sub_plain.txt","w").write(f"# Lejopka | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | {len(final)} серверов\n"+"\n".join(final))
  open("README.md","w").write(f"# ⚡ Lejopka VPN\n\nПодписка для Happ:\n```\nhttps://raw.githack.com/lejopka/lejopka/main/sub.txt\n```\n**Серверов:** {len(final)}\n**Обновлено:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n## Как добавить\n1. Скопируй ссылку\n2. Happ → **+** → **URL подписки** → вставь\n")
  print("Сохранено!")
