import React from 'react';
import {AbsoluteFill, Audio, Composition, Img, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from './timeline.json';

const mint = '#a6f3cb';
const muted = '#9caebd';
type SceneData = typeof timeline.scenes[number];
const base: React.CSSProperties = {backgroundColor:'#09131c',color:'#f5f7f3',fontFamily:'Arial, Helvetica, sans-serif'};

const Board: React.FC = () => {
  const f = useCurrentFrame();
  return <div style={{width:740,height:650,display:'flex',alignItems:'center',justifyContent:'center',position:'relative'}}>
    <div style={{position:'absolute',inset:35,border:'1px solid #29433e',borderRadius:40,background:'radial-gradient(ellipse at center, #133c35 0%, #0b1921 72%)'}}/>
    <Img src={staticFile('assets/board.svg')} style={{width:650,height:550,objectFit:'contain',transform:`rotate(-7deg) scale(${1+Math.min(f,500)/16000})`,filter:'drop-shadow(0 24px 25px #0009)'}}/>
    <div style={{position:'absolute',bottom:22,color:muted,fontSize:18,letterSpacing:3}}>ACTUAL PCB LAYOUT · NOT A PHOTOGRAPH</div>
  </div>;
};

const Panel: React.FC<{scene:SceneData}> = ({scene}) => {
  const f = useCurrentFrame();
  if(scene.kind==='board') return <Board/>;
  if(scene.kind==='targets') return <div style={{width:700,display:'flex',flexDirection:'column',gap:24}}>{[['F071','INITIAL TARGET',mint],['F072','BOARD OPTION · SOFTWARE NOT IMPLEMENTED','#e4b985']].map(([name,label,color],i)=><div key={name} style={{padding:'45px 42px',borderRadius:22,border:`1px solid ${color}66`,background:'#11232e',opacity:interpolate(f,[i*12,i*12+20],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><div style={{fontSize:90,color,fontWeight:800}}>{name}</div><div style={{fontSize:24,color:muted,marginTop:16}}>{label}</div></div>)}</div>;
  if(scene.kind==='code') return <div style={{width:710,border:'1px solid #304553',borderRadius:24,overflow:'hidden',background:'#0d1e29'}}><div style={{padding:'22px 35px',background:'#19303b',color:muted,fontSize:24}}>Blink.ino</div><pre style={{fontSize:28,lineHeight:1.65,padding:'25px 35px',color:mint}}>{`void setup() {\n  pinMode(LED_BUILTIN, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(LED_BUILTIN, LOW);\n  delay(500);\n  digitalWrite(LED_BUILTIN, HIGH);\n  delay(500);\n}`}</pre><div style={{padding:'5px 35px 30px',display:'flex',gap:15,alignItems:'center',color:muted,fontSize:22}}><span style={{width:20,height:20,borderRadius:'50%',background:Math.floor(f/15)%2===0?mint:'#29423a'}}/>LOW = on · HIGH = off</div></div>;
  if(scene.kind==='pins') return <div style={{width:700,display:'flex',flexDirection:'column',gap:25}}>{[['UART','D2  TX →','D0  RX ←'],['I²C','SDA','SCL'],['I/O','3.3 V','Check shields']].map(([bus,a,b],i)=><div key={bus} style={{background:'#11232e',borderLeft:`5px solid ${mint}`,borderRadius:12,padding:30,transform:`translateX(${interpolate(f,[i*10,i*10+20],[60,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}px)`}}><div style={{fontSize:23,color:muted,marginBottom:16}}>{bus}</div><div style={{display:'flex',justifyContent:'space-between',fontSize:40,fontWeight:700}}><span>{a}</span><span style={{color:mint}}>{b}</span></div></div>)}</div>;
  return <div style={{width:700,background:'#211f22',border:'1px solid #665444',padding:48,borderRadius:24}}><div style={{color:'#e4b985',fontSize:27}}>JP3 · POWER DISCONNECTED</div><div style={{display:'flex',justifyContent:'space-around',margin:'55px 0 35px'}}>{['1','2','3'].map((pin,i)=><div key={pin} style={{textAlign:'center'}}><div style={{width:105,height:105,borderRadius:'50%',border:`7px solid ${i>0?mint:'#65717b'}`,background:i>0?'#285346':'#18242c',display:'grid',placeItems:'center',fontSize:42}}>{pin}</div><div style={{fontSize:25,color:muted,marginTop:20}}>{['5 V','VCC','3.3 V'][i]}</div></div>)}</div><div style={{fontSize:35,lineHeight:1.65}}><span style={{color:'#e4b985'}}>Open 1–2.</span><br/><span style={{color:mint}}>Bridge 2–3.</span></div><div style={{fontSize:23,color:muted,marginTop:20,lineHeight:1.5}}>Connection diagram only — verify pad identity in the guide. Not a physical orientation.</div></div>;
};

const Scene: React.FC<{scene:SceneData,index:number}> = ({scene,index}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig();
  const enter = spring({frame,fps,config:{damping:200}});
  const caption = scene.captions.find(c=>frame/fps>=c.start && frame/fps<c.end);
  return <AbsoluteFill style={{...base,padding:'85px 95px'}}>
    <div style={{position:'absolute',top:0,left:0,width:1920,height:4,background:'#203740'}}><div style={{height:4,background:mint,width:`${100*(scene.from+frame)/timeline.durationInFrames}%`}}/></div>
    <div style={{display:'flex',justifyContent:'space-between',fontSize:22,letterSpacing:4,color:muted}}><span>MICROPETAL / FIELD NOTES</span><span>{String(index+1).padStart(2,'0')} / 06</span></div>
    <div style={{display:'flex',alignItems:'center',gap:60,flex:1,marginTop:25,marginBottom:130,opacity:enter,transform:`translateY(${(1-enter)*30}px)`}}>
      <div style={{width:900}}><div style={{color:mint,fontSize:23,letterSpacing:3,marginBottom:28}}>{scene.eyebrow}</div><h1 style={{fontSize:80,lineHeight:1.07,letterSpacing:-3,whiteSpace:'pre-line',margin:'0 0 40px',fontWeight:800}}>{scene.title}</h1><div style={{display:'flex',flexDirection:'column',gap:17}}>{scene.labels.map((label,i)=><div key={label} style={{fontSize:28,color:muted,opacity:interpolate(frame,[18+i*9,35+i*9],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>— {label}</div>)}</div></div><Panel scene={scene}/>
    </div>
    <div style={{position:'absolute',bottom:78,left:170,right:170,minHeight:90,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',fontSize:31,lineHeight:1.35,color:'#e9eeec'}}>{caption?.text}</div>
    <div style={{position:'absolute',bottom:25,left:95,right:95,display:'flex',justifyContent:'space-between',fontSize:18,color:muted}}><span>github.com/AndersBNielsen/MicroPetal</span><span>EXPERIMENTAL · HARDWARE VALIDATION PENDING</span></div>
    <Audio src={staticFile(scene.audio)}/>
  </AbsoluteFill>;
};
const Explainer: React.FC = () => <AbsoluteFill style={base}>{timeline.scenes.map((scene,index)=><Sequence key={scene.id} from={scene.from} durationInFrames={scene.durationInFrames}><Scene scene={scene} index={index}/></Sequence>)}</AbsoluteFill>;
const Thumbnail: React.FC = () => <AbsoluteFill style={{...base,padding:100,display:'flex',flexDirection:'row',alignItems:'center'}}><div style={{width:950}}><div style={{color:mint,fontSize:32,letterSpacing:6}}>MEET MICROPETAL</div><h1 style={{fontSize:128,lineHeight:1,margin:'30px 0'}}>Familiar shape.<br/><span style={{color:mint}}>Different heart.</span></h1><div style={{fontSize:34,color:muted}}>PY32 · Uno-format · Open hardware</div></div><Board/></AbsoluteFill>;
const Root: React.FC = () => <><Composition id="MicroPetal" component={Explainer} durationInFrames={timeline.durationInFrames} fps={timeline.fps} width={timeline.width} height={timeline.height}/><Composition id="Thumbnail" component={Thumbnail} durationInFrames={1} fps={30} width={1920} height={1080}/></>;
registerRoot(Root);
