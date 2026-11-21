#!/usr/bin/env python3
"""Check board table and vector table against analyzed CAD/device sources; no USB access."""
from pathlib import Path
import argparse,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];core=root/'hardware/micropetal/py32/cores/micropetal'
expected=['PB0','PB1','PB2','PB3','PB4','PB5','PB6','PB7','PB8','PB9','PB12','PB15','PB14','PB13']+['PA'+str(i) for i in range(8)]+['PB11','PB10']
actual=['P'+port+bit for port,bit in re.findall(r'\{GPIO([AB]),1<<(\d+)\}',(core/'wiring.cpp').read_text().split('static int')[0])]
assert actual==expected,(actual,expected)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--netlist',type=Path,help='KiCad XML netlist to check against the core')
args=parser.parse_args()
cad=args.netlist if args.netlist else root/'schematic.net.xml'
if args.netlist and not cad.is_file():parser.error('Netlist does not exist: '+str(cad))
if cad.exists():
 nets=ET.parse(cad).getroot().findall('./nets/net')
 header={str(i):'D'+str(i-15) for i in range(15,29)}
 header.update({'9':'A0','10':'A1','11':'A2','12':'A3','13':'A4','14':'A5','30':'A6','1':'A7','31':'SDA','32':'SCL'})
 names=['D'+str(i) for i in range(14)]+['A'+str(i) for i in range(8)]+['SDA','SCL'];observed={}
 for net in nets:
  labels=[header[n.get('pin')] for n in net if n.get('ref')=='A1' and n.get('pin') in header]
  mcus=[n.get('pinfunction').split('_')[0] for n in net if n.get('ref')=='U1']
  for label in labels:
   assert len(mcus)==1,(label,mcus)
   observed[label]=mcus[0]
 assert [observed[n] for n in names]==expected,observed
irq={int(n):name+'_IRQHandler' for name,n in re.findall(r'(\w+)_IRQn\s*=\s*(\d+)',(core/'device/py32f071xB.h').read_text())}
vector=(core/'startup.S').read_text().split('g_pfnVectors:')[1]
entries=re.findall(r'\.word\s+(\w+)',vector)
assert len(entries)==48
for i in range(32):assert entries[16+i]==irq.get(i,'0'),(i,entries[16+i],irq.get(i))
assert entries[0]=='_estack' and entries[1]=='Reset_Handler'
assert '128K' in (root/'hardware/micropetal/py32/variants/micropetal_uno/linker.ld').read_text()
print('PASS: 24 header pin mappings and 32 F071 peripheral IRQ slots')
