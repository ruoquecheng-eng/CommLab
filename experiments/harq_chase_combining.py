from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import ConvolutionalCode
from commlab.link import append_crc16,check_crc16,ChaseCombiner
from commlab.modulation import QAMModem

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def qam_labels(modem):
    return ((np.arange(modem.order)[:,None] >> np.arange(modem.bits_per_symbol-1,-1,-1)) & 1).astype(np.uint8)


def flat_fading_llr(y,h,const,labels,noise_var):
    d2=np.abs(np.asarray(y)[:,None]-complex(h)*const[None,:])**2
    out=np.empty((len(y),labels.shape[1]))
    for b in range(labels.shape[1]):
        d0=np.min(d2[:,labels[:,b]==0],axis=1); d1=np.min(d2[:,labels[:,b]==1],axis=1)
        out[:,b]=(d1-d0)/noise_var
    return out.reshape(-1)


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(9021); modem=QAMModem(4); labels=qam_labels(modem); const=modem.modulate(labels.reshape(-1)); code=ConvolutionalCode()
    snrs=[-4,-2,0,2,4,6]; n_packets=120; payload_len=160; max_tx=4
    rows=[]
    for snr_db in snrs:
        nv=10**(-snr_db/10)
        stats={m:{'ok':0,'tx':0,'lat':[]} for m in ['Type-I HARQ','Chase combining']}
        for _ in range(n_packets):
            payload=rng.integers(0,2,payload_len,dtype=np.uint8); frame=append_crc16(payload); coded=code.encode(frame,terminate=True); x=modem.modulate(coded)
            active={m:True for m in stats}; comb=ChaseCombiner(len(coded))
            for attempt in range(1,max_tx+1):
                h=(rng.normal()+1j*rng.normal())/np.sqrt(2)
                y=h*x+np.sqrt(nv/2)*(rng.normal(size=len(x))+1j*rng.normal(size=len(x)))
                llr=flat_fading_llr(y,h,const,labels,nv)
                # Type-I: discard old observation
                if active['Type-I HARQ']:
                    stats['Type-I HARQ']['tx']+=1
                    dec=code.decode_soft(llr,terminated=True,trim_tail=True)
                    if check_crc16(dec): stats['Type-I HARQ']['ok']+=1; stats['Type-I HARQ']['lat'].append(attempt); active['Type-I HARQ']=False
                if active['Chase combining']:
                    stats['Chase combining']['tx']+=1
                    dec=code.decode_soft(comb.add(llr),terminated=True,trim_tail=True)
                    if check_crc16(dec): stats['Chase combining']['ok']+=1; stats['Chase combining']['lat'].append(attempt); active['Chase combining']=False
                if not any(active.values()): break
        symbols_per_tx=len(x)
        for m,s in stats.items():
            success=s['ok']/n_packets; avg_tx=s['tx']/n_packets; goodput=(s['ok']*payload_len)/(s['tx']*symbols_per_tx) if s['tx'] else 0
            mean_latency=np.mean(s['lat']) if s['lat'] else np.nan
            rows.append((snr_db,m,success,1-success,avg_tx,goodput,mean_latency,s['ok'],s['tx']))
        print(f'{snr_db:>2} dB  Type-I success={stats["Type-I HARQ"]["ok"]/n_packets:.3f} tx={stats["Type-I HARQ"]["tx"]/n_packets:.2f} | Chase success={stats["Chase combining"]["ok"]/n_packets:.3f} tx={stats["Chase combining"]["tx"]/n_packets:.2f}')
    with open(DATA/'harq_chase_combining.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','scheme','success_probability','packet_error_rate','average_transmissions','payload_goodput_bits_per_qpsk_symbol','mean_success_latency_attempts','successful_packets','transmissions']); w.writerows(rows)
    plt.figure(figsize=(7.5,4.9))
    for m in ['Type-I HARQ','Chase combining']:
        q=np.array([[r[0],r[3]] for r in rows if r[1]==m],float); plt.semilogy(q[:,0],np.maximum(q[:,1],1/n_packets/3),'o-',label=m)
    plt.xlabel('Average SNR per transmission (dB)'); plt.ylabel('Packet error probability after max 4 transmissions'); plt.title('CRC-Gated HARQ Reliability over Block Rayleigh Fading'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'harq_packet_error.png',dpi=180); plt.close()
    plt.figure(figsize=(7.5,4.9))
    for m in ['Type-I HARQ','Chase combining']:
        q=np.array([[r[0],r[5]] for r in rows if r[1]==m],float); plt.plot(q[:,0],q[:,1],'o-',label=m)
    plt.xlabel('Average SNR per transmission (dB)'); plt.ylabel('Delivered payload bits / transmitted QPSK symbol'); plt.title('HARQ Goodput Including Retransmission Cost'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'harq_goodput.png',dpi=180); plt.close()

if __name__=='__main__': main()
