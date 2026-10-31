// Canonical local delivery layout. Each folder contains one platform's posting kit.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const settings=()=>JSON.parse(fs.readFileSync(path.join(root,'config/publishing-channels.json'),'utf8'));
const slug=(value,label)=>{if(typeof value!=='string'||!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value))throw Error(`Invalid ${label}`);return value;};
function deliveryPaths(job,override={}){
 const config=settings(),m=job.metadata||{},platform=slug(String(override.platform||m.platform||'').toLowerCase(),'platform');
 if(!config.platforms[platform])throw Error('Unknown platform: '+platform);
 const id=slug(job.id,'job ID');
 const parts=[config.outputRoot,platform];
 if(platform!=='youtube'){
  const channel=slug(override.channelId||m.channelId,'channel');
  if(!Object.hasOwn(config.platforms[platform].channels,channel))throw Error('Unknown channel: '+channel);
  parts.push(channel);
 }
 const outputRoot=config.outputRoot;if(outputRoot!=='output')throw Error('Expected workspace output root');
 const deliveryDir=path.posix.join(...parts,id);
 return {deliveryDir,output:deliveryDir+'/video.mp4',post:deliveryDir+'/bai-viet.md',cover:deliveryDir+'/poster.png',subtitles:deliveryDir+'/phu-de.srt',credits:deliveryDir+'/ghi-cong.txt',previewDir:deliveryDir+'/previews',manifest:deliveryDir+'/manifest.json'};
}
function previewsFor(job){return job.metadata.previewDir||deliveryPaths(job).previewDir;}
function writeDeliveryManifest(job,delivery=job.metadata){
 const dir=delivery.deliveryDir||deliveryPaths(job,delivery).deliveryDir;
 const absolute=path.resolve(root,dir);if(!absolute.startsWith(path.join(root,'output')+path.sep))throw Error('Outside output');
 fs.mkdirSync(path.join(absolute,'metadata'),{recursive:true});
 fs.writeFileSync(path.join(absolute,'metadata/job.json'),JSON.stringify({...job,metadata:{...job.metadata,...delivery}},null,2)+'\n');
 const walk=folder=>fs.readdirSync(folder,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(folder,e.name)):[path.join(folder,e.name)]);
 const files=walk(absolute).filter(f=>f!==path.join(absolute,'manifest.json')).map(f=>({file:path.relative(absolute,f).split(path.sep).join('/'),bytes:fs.statSync(f).size}));
 const content={jobId:job.id,title:job.title,platform:delivery.platform||job.metadata.platform,channelId:delivery.channelId||null,status:'prepared-not-published',sourceJob:`jobs/${job.id}.json`,files};
 fs.writeFileSync(path.join(absolute,'manifest.json'),JSON.stringify(content,null,2)+'\n');
 return dir+'/manifest.json';
}
module.exports={deliveryPaths,previewsFor,writeDeliveryManifest};
if(require.main===module){
 const file=process.argv[2];if(!file)throw Error('Usage: node scripts/output-layout.cjs jobs/<job>.json');
 const absolute=path.resolve(root,file);if(!absolute.startsWith(root+path.sep))throw Error('Outside workspace');
 console.log(JSON.stringify(deliveryPaths(JSON.parse(fs.readFileSync(absolute,'utf8'))),null,2));
}
