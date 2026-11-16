// Uso: node render.mjs video   -> gera frames e MP4 (sem áudio) em out/video_noaudio.mp4
//      node render.mjs stills DIR t1 t2 ...  -> capturas em instantes específicos
//      node render.mjs timeline -> imprime a linha do tempo (JSON)
import { createRequire } from 'module';
import { spawn } from 'child_process';
import path from 'path'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const mode = process.argv[2];
const FPS = 30;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.addInitScript(() => { window.__CAPTURE = true; });
await page.goto('file://' + path.join(here, 'video.html'));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
const tl = await page.evaluate(() => window.__TIMELINE);
if (mode === 'timeline') { console.log(JSON.stringify(tl)); }
else if (mode === 'stills') {
  const dir = process.argv[3]; fs.mkdirSync(dir, { recursive: true });
  for (const t of process.argv.slice(4)) {
    await page.evaluate(t => window.__render(t), +t);
    await page.screenshot({ path: path.join(dir, `t${String(t).padStart(6, '0')}.png`) });
  }
} else if (mode === 'video') {
  fs.mkdirSync(path.join(here, 'out'), { recursive: true });
  fs.writeFileSync(path.join(here, 'out', 'timeline.json'), JSON.stringify(tl));
  const n = Math.round(tl.total * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(here, 'out', 'video_noaudio.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.__render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log('done', n, 'frames');
}
await browser.close();
