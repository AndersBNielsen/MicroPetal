import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {mkdir, readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('..',import.meta.url));
process.chdir(root);
await mkdir('out',{recursive:true});
const timeline = JSON.parse(await readFile('src/timeline.json','utf8'));
const serveUrl = await bundle({entryPoint:path.join(root,'src/index.tsx'),publicDir:path.join(root,'public')});
// Use installed Chrome; avoid downloading a second browser on this workstation.
const browserExecutable = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const options = {serveUrl,browserExecutable};
const composition = await selectComposition({...options,id:'MicroPetal'});
let previous = -1;
await renderMedia({...options,composition,codec:'h264',audioCodec:'aac',crf:18,outputLocation:'out/micropetal-explainer.mp4',concurrency:4,onProgress:({progress})=>{const pct=Math.floor(progress*10)*10;if(pct!==previous){console.log(`Render ${pct}%`);previous=pct;}}});
execFileSync('python3',['scripts/master-narration.py'],{stdio:'inherit'});
const thumbnail = await selectComposition({...options,id:'Thumbnail'});
await renderStill({...options,composition:thumbnail,output:'out/thumbnail.png'});
for (const scene of timeline.scenes) {
  await renderStill({...options,composition,frame:scene.from+Math.min(75,scene.durationInFrames-1),output:`out/scene-${scene.id}.png`});
}
console.log('Rendered MP4, thumbnail, and editorial review stills.');
