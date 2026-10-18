const fs=require('fs'),path=require('path'),{execFileSync,spawnSync}=require('child_process');
const ffmpeg=require('ffmpeg-static'),ffprobe=require('ffprobe-static').path;
const root=process.cwd();
const local=rel=>{const p=path.resolve(root,rel);if(!p.startsWith(root+path.sep))throw Error('Path outside workspace');return p;};
const job=JSON.parse(fs.readFileSync(local(process.argv[2]),'utf8'));
const info=file=>JSON.parse(execFileSync(ffprobe,['-v','error','-show_format','-show_streams','-of','json',local(file)],{encoding:'utf8'}));
const input=job.metadata.output,format=info(input),v=format.streams.find(s=>s.codec_type==='video'),a=format.streams.find(s=>s.codec_type==='audio');
if(!fs.statSync(local(input)).size||v?.codec_name!=='h264'||a?.codec_name!=='aac'||v.width!==job.format.width||v.height!==job.format.height||Math.abs(Number(format.format.duration)-job.format.durationInFrames/job.format.fps)>.1)throw Error('Output format mismatch');
if(Math.abs(evalRate(v.avg_frame_rate)-job.format.fps)>.001)throw Error('FPS mismatch');
function evalRate(rate){const [n,d]=rate.split('/').map(Number);return n/d;}
if(job.scenes.reduce((n,s)=>n+s.durationInFrames,0)!==job.format.durationInFrames)throw Error('Timeline mismatch');
for(const [i,s]of job.scenes.entries()){for(const f of s.assets)if(!fs.existsSync(local(f)))throw Error('Missing '+f);if(s.audio){const duration=Number(info(s.audio).format.duration);if(duration+.25>s.durationInFrames/job.format.fps||Math.abs(duration-job.metadata.timings[i].voiceDuration)>.025)throw Error('Voice timeline mismatch');}}
for(const c of job.metadata.captions)if(c.start<0||c.end<=c.start||c.end>job.format.durationInFrames/job.format.fps)throw Error('Caption timing mismatch');
function stats(file,start,duration){const r=spawnSync(ffmpeg,['-hide_banner','-ss',String(start),'-t',String(duration),'-i',local(file),'-vn','-af','volumedetect','-f','null','-'],{encoding:'utf8'});if(r.status)throw Error(r.stderr);return {meanDb:Number(r.stderr.match(/mean_volume: ([-\d.]+)/)[1]),peakDb:Number(r.stderr.match(/max_volume: ([-\d.]+)/)[1])};}
const duration=job.format.durationInFrames/job.format.fps,last=job.metadata.timings.at(-1);
const silentGaps=job.metadata.timings.map((t,i,list)=>({start:t.voiceDuration?t.voiceStart+t.voiceDuration+.4:t.from/job.format.fps+.2,end:i+1<list.length?list[i+1].voiceStart:duration-.3})).filter(g=>g.end-g.start>=1.2);
if(!silentGaps.length)throw Error('No music-only interval for verification');
const musicGap=silentGaps[0];
const levels={mix:stats(input,0,duration),voice:stats(job.metadata.voiceStem,.3,Math.min(duration-3,30)),musicUnderVoice:stats(job.metadata.musicStem,.3,Math.min(duration-3,30)),musicOnly:stats(input,musicGap.start,1.2)};
if(levels.mix.peakDb>-.5||levels.musicOnly.meanDb<-28||levels.voice.meanDb<levels.musicUnderVoice.meanDb+3)throw Error('Audio balance failed');
const cover=info(job.metadata.cover);if(cover.streams[0].width!==job.format.width||cover.streams[0].height!==job.format.height)throw Error('Cover size mismatch');
if(!fs.existsSync(local(job.metadata.post)))throw Error('Post missing');
const dir=`output/previews/${job.metadata.projectId}`;
const frames=job.metadata.timings.map(t=>t.from+Math.min(Math.round(t.duration*.56),t.duration-1));
const sheet=`${dir}/${job.id}-contact.jpg`;
execFileSync(ffmpeg,['-v','error','-n','-i',local(input),'-vf','select='+frames.map(n=>`eq(n\\,${n})`).join('+')+',scale=270:480,tile=4x2','-frames:v','1',local(sheet)]);
for(const [label,frame]of [['first',0],['last',job.format.durationInFrames-1]])execFileSync(ffmpeg,['-v','error','-n','-ss',String(frame/job.format.fps),'-i',local(input),'-frames:v','1',local(`${dir}/${job.id}-${label}.png`)]);
const report={verified:true,output:input,size:fs.statSync(local(input)).size,format,levels,cover:job.metadata.cover,post:job.metadata.post,limitations:job.metadata.assumptions,subjectiveListening:false};
const reportPath=`temp/${job.id}/verification.json`;fs.mkdirSync(path.dirname(local(reportPath)),{recursive:true});fs.writeFileSync(local(reportPath),JSON.stringify(report,null,2),{flag:'wx'});
console.log(JSON.stringify({verified:true,seconds:format.format.duration,bytes:report.size,levels,cover:report.cover,post:report.post}));
