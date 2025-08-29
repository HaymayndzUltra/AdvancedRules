#!/usr/bin/env python3
import argparse, re, sys, time, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--p95-ms', type=float, default=1200.0)
args = parser.parse_args()

def scrape(url):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode()

def parse_histogram(lines, name, label_key='persona'):
    # returns {persona: (buckets{le:count}, total_count)}
    buckets = {}
    totals = {}
    for ln in lines:
        if ln.startswith(f"{name}_bucket"):
            labs = ln.split("{",1)[1].split("}",1)[0]
            val = float(ln.rsplit(" ",1)[1])
            le = re.search(r'le="([^"]+)"', labs).group(1)
            persona = re.search(fr'{label_key}="([^"]+)"', labs).group(1)
            buckets.setdefault(persona, {})[float(le)] = val
        elif ln.startswith(f"{name}_count"):
            labs = ln.split("{",1)[1].split("}",1)[0]
            val = float(ln.rsplit(" ",1)[1])
            persona = re.search(fr'{label_key}="([^"]+)"', labs).group(1)
            totals[persona] = totals.get(persona, 0.0) + val
    return {p:(buckets.get(p,{}), totals.get(p,0.0)) for p in set(buckets)|set(totals)}

def p95_from_hist(buckets, total):
    if total == 0: return None
    target = 0.95 * total
    for le in sorted(buckets.keys()):
        if buckets[le] >= target:
            return le
    return None

text = scrape(args.url).splitlines()

# Counters must move
c_started = sum(float(l.rsplit(" ",1)[1]) for l in text if l.startswith("ar_flow_started_total"))
c_success = sum(float(l.rsplit(" ",1)[1]) for l in text if l.startswith("ar_flow_success_total"))
if c_started < 1 or c_success < 1:
    print(f"✗ counters too low: started={c_started}, success={c_success}")
    sys.exit(1)

# P95 check
hist = parse_histogram(text, "ar_step_latency_ms")
violations = []
for persona, (bkt, tot) in hist.items():
    p95 = p95_from_hist(bkt, tot)
    if p95 is None:
        continue
    if p95 > args.p95_ms:
        violations.append((persona, p95, tot))

if violations:
    for v in violations:
        print(f"✗ P95 too high: persona={v[0]} p95={v[1]}ms n={int(v[2])}")
    sys.exit(1)

print(f"✓ metrics ok: started={int(c_started)} success={int(c_success)} (p95<= {args.p95_ms} ms)")
