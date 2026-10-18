// Local Remotion renderer: node scripts/render-job.cjs jobs/<job>.json preview|render
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const root=process.cwd();
const local=rel=>{const p=path.resolve(root,rel);if(!p.startsWith(root+path.sep))throw Error('Outside workspace');return p;};
const [jobFile,mode='preview']=process.argv.slice(2);
if(!jobFile||!['preview','render','render-video'].includes(mode))throw Error('Usage: render-job.cjs jobs/<job>.json preview|render|render-video');
const job=JSON.parse(fs.readFileSync(local(jobFile),'utf8'));
if(!/^[a-z0-9-]+$/.test(job.id)||!/^[a-z0-9-]+$/.test(job.metadata.projectId))throw Error('Invalid job/project ID');
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const hash=crypto.createHash('sha256');for(const f of [local(jobFile),...walk(local('src')).filter(f=>/\.(ts|tsx)$/.test(f))])hash.update(fs.readFileSync(f));
const revision=hash.digest('hex').slice(0,10),tmp=local('temp/'+job.id),publicDir=path.join(tmp,'public-'+revision),bundleDir=path.join(tmp,'bundle-'+revision);
async function main(){
 fs.mkdirSync(publicDir,{recursive:true});
 const files=[...new Set([job.metadata.logo,job.metadata.mix,...job.scenes.flatMap(s=>s.assets)].filter(Boolean))];
 for(const file of files){if(!file.startsWith('assets/'))throw Error('Expected asset path');const source=local(file),dest=path.resolve(publicDir,file.slice(7));if(!dest.startsWith(publicDir+path.sep))throw Error('Unsafe public path');fs.mkdirSync(path.dirname(dest),{recursive:true});if(!fs.existsSync(dest))fs.copyFileSync(source,dest,fs.constants.COPYFILE_EXCL);}
 const serveUrl=fs.existsSync(path.join(bundleDir,'index.html'))?bundleDir:await bundle({entryPoint:local('src/index.ts'),outDir:bundleDir,publicDir,rootDir:root,onProgress:p=>{if(p===100)console.log('Bundle ready');}});
 const browser=await openBrowser('chrome',{browserExecutable:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const composition=await selectComposition({serveUrl,id:job.metadata.compositionId,puppeteerInstance:browser});
  const cover=job.metadata.coverCompositionId?await selectComposition({serveUrl,id:job.metadata.coverCompositionId,puppeteerInstance:browser}):null;
  if(mode==='preview'){
   const dir=local(`output/previews/${job.metadata.projectId}/${job.id}-review-${revision}`);if(fs.existsSync(dir))throw Error('Review directory exists');fs.mkdirSync(dir,{recursive:true});
   for(const [i,t]of job.metadata.timings.entries()){const frame=t.from+Math.min(Math.round(t.duration*.56),t.duration-1);await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.join(dir,`scene-${i+1}.png`),imageFormat:'png',overwrite:false});console.log('Preview '+(i+1));}
   if(cover)await renderStill({serveUrl,composition:cover,puppeteerInstance:browser,frame:0,output:path.join(dir,'cover.png'),imageFormat:'png',overwrite:false});console.log('Review '+path.relative(root,dir));
  }else{
   if(fs.existsSync(local(job.metadata.output))||mode==='render'&&job.metadata.cover&&fs.existsSync(local(job.metadata.cover)))throw Error('Output exists; use a new version');
   let last=-1;await renderMedia({serveUrl,composition,puppeteerInstance:browser,outputLocation:local(job.metadata.output),codec:'h264',audioCodec:'aac',pixelFormat:'yuv420p',crf:19,concurrency:4,overwrite:false,onProgress:p=>{const n=Math.floor(p.progress*10);if(n!==last){last=n;console.log(`Render ${Math.round(p.progress*100)}%`);}}});
   if(cover&&mode==='render')await renderStill({serveUrl,composition:cover,puppeteerInstance:browser,frame:0,output:local(job.metadata.cover),imageFormat:'png',overwrite:false});
   console.log('Finished '+job.metadata.output);
  }
 }finally{await browser.close({silent:true});}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
