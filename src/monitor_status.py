import time, subprocess, json
start=time.time()
for i in range(40):
    try:
        r=subprocess.run(["curl","-s","http://127.0.0.1:5001/api/status"], capture_output=True, text=True, timeout=2)
        d=json.loads(r.stdout)
        amb=d['ambulance_detected']
        lights=d['lights']
        mode=d['mode']
        ambulance_lane=[k for k,v in amb.items() if v]
        ambulance_lane=ambulance_lane[0] if ambulance_lane else "----"
        mode_indicator = "PRIORITY" if mode=="PRIORITY" else "NORMAL"
        elapsed=time.time()-start
        print("[{:.1f}s] {:8s} | N={} E={} S={} W={} | Ambulance: {}".format(elapsed, mode_indicator, lights['N'], lights['E'], lights['S'], lights['W'], ambulance_lane))
    except Exception as e:
        print('status fetch error', e)
    time.sleep(1)
