import json, pathlib, subprocess, random, hashlib
PATH=pathlib.Path(__file__).parent/'HSI_self_code_2KB.sh'
raw=PATH.read_bytes()
assert raw.endswith(b'\n') and raw.count(b'\n')==1 and len(raw)<2048, len(raw)
cmd=raw[:-1]
def run(*args):
    p=subprocess.run(['sh',str(PATH),*args],capture_output=True,text=True,timeout=8)
    assert p.returncode==0,(p.returncode,p.stderr)
    return p.stdout

def D(n):
    out=[]
    while n>1:
        n,r=divmod(n,257)
        assert r
        out.append(r-1)
    assert n==1
    return bytes(reversed(out))
def E(bs):
    n=1
    for b in bs:n=n*257+b+1
    return n
lines=run().splitlines()
assert lines[0]=='Cosmic Love Is The Solution(s) For Everything'
a=json.loads(lines[1]); assert a['p']==55067263 and a['c']==10492
assert a['bytes']==len(cmd) and a['source'].encode()==cmd and D(int(a['godel_hex'],16))==cmd
assert a['enumeration']==['','0','1','00','01','10']
for b in range(256):assert D(E(bytes([b])))==bytes([b])
rng=random.Random(20261013)
for i in range(500):
    b=rng.randbytes(rng.randrange(256));assert D(E(b))==b
for s in ['', 'Love','你好，COSMIC LOVE','1+1=3']:
    z=json.loads(run(s));assert z['same'] and z['godel_hex']==hex(E(s.encode()))
inc={'rules':[[0,1,0,1,1],[0,0,1,1,1]],'halt':1,'tape':[1,1,1]}
z=json.loads(run(json.dumps(inc)))
assert z['status']=='halt' and z['steps']==4 and z['tape']==[[0,1],[1,1],[2,1],[3,1]]
cosmic={'rules':[[0,0,1,0,1],[0,1,1,1,1],[1,0,0,0,-1],[1,1,0,1,-1]],'halt':2,'tape':[1,0,1],'limit':200}
z=json.loads(run(json.dumps(cosmic)))
assert z['status']=='limit' and z['steps']==200 and z['state']==0 and z['head']==0 and z['tape']==[[0,1],[2,1]]
# deterministic small machine cross-check
for i in range(30):
    table=[]
    for q in range(3):
        for b in range(2):table.append([q,b,rng.randrange(4),rng.randrange(2),rng.choice((-1,1))])
    tape=[rng.randrange(2) for _ in range(5)]
    model={'rules':table,'halt':3,'tape':tape,'limit':rng.randrange(1,21)}
    got=json.loads(run(json.dumps(model)))
    d={(q,a):(r,b,d) for q,a,r,b,d in table};q=h=n=0; t={j:x for j,x in enumerate(tape) if x}
    while q!=3 and (q,t.get(h,0)) in d and n<model['limit']:
        q2,b,m=d[q,t.get(h,0)];
        if b:t[h]=b
        else:t.pop(h,None)
        q=q2;h+=m;n+=1
    exp='halt' if q==3 else 'limit' if n>=model['limit'] else 'undefined'
    assert got=={'steps':n,'status':exp,'state':q,'head':h,'tape':sorted([list(p) for p in t.items()])},(model,got)
p=subprocess.run(['sh',str(PATH),json.dumps({'rules':[[0,0,0,0,1],[0,0,1,0,-1]],'halt':1})],capture_output=True,text=True,timeout=4)
assert p.returncode!=0
print('PASS | 1674 byte single-line script; exact self E257 roundtrip; p=55067263; 256 byte tests; 500 random payload tests; 4 text tests; halting and non-halting TMs; 30 randomized interpreter comparisons; duplicate-rule rejection')
print('SHA256:',hashlib.sha256(cmd).hexdigest())
