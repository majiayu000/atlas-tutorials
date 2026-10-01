#!/usr/bin/env python3
"""Build a self-contained local reader. Optional authoring dependency: markdown-it-py."""
from pathlib import Path
import html
import json
import re
import urllib.parse
from markdown_it import MarkdownIt
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'catalog.json').read_text())
MD=MarkdownIt('commonmark',{'html':False}).enable('table')
files=[ROOT/'README.md',*[ROOT/i['path'] for i in CAT],ROOT/'CATALOG.md',ROOT/'common/EXECUTION.md',ROOT/'common/DELIVERY.md',ROOT/'SOURCES.md',ROOT/'verification/REPORT.md',ROOT/'PUBLISHING.md',ROOT/'scripts/README.md',ROOT/'third-party/README.md']
ids={f.resolve():('home' if f.name=='README.md' and f.parent==ROOT else 'doc-'+f.relative_to(ROOT).as_posix().replace('/','--').replace('.','-')) for f in files}
guides={
 (ROOT/'tutorials/02-first-image.md').resolve(): ('02-first-image.html', 'Atlas CLI 生成第一张图片并保存任务回执'),
 (ROOT/'tutorials/19-image-to-video.md').resolve(): ('19-image-to-video.html', 'Atlas 图生视频：提交、续查与视频验收'),
 (ROOT/'tutorials/43-recover-job.md').resolve(): ('43-recover-job.html', 'Atlas 生成超时或下载失败：继续原任务'),
}

def render(f, standalone=False):
 tokens=MD.parse(f.read_text())
 for token in tokens:
  for c in token.children or []:
   if c.type not in ['link_open','image']:continue
   attr='href' if c.type=='link_open' else 'src';v=c.attrGet(attr)
   if not v or urllib.parse.urlsplit(v).scheme or v.startswith('#'):continue
   target=(f.parent/urllib.parse.unquote(v.split('#')[0])).resolve()
   if target in ids:
    if standalone:
     c.attrSet(attr, guides[target][0] if target in guides else '../index.html#'+ids[target])
    else:c.attrSet(attr,'#'+ids[target])
   else:
    try:c.attrSet(attr,('../' if standalone else '')+target.relative_to(ROOT).as_posix())
    except ValueError:pass
 return MD.renderer.render(tokens,MD.options,{})
nav=['<a class="home-link" href="#home">使用说明与离线演练</a>']
for category in dict.fromkeys(i['category'] for i in CAT):
 nav.append('<div class="nav-group"><h3>'+html.escape(category)+'</h3>')
 for i in CAT:
  if i['category'] != category:continue
  key=ids[(ROOT/i['path']).resolve()]
  nav.append(f'<a class="lesson-link" data-target="{key}" href="#{key}"><span>{i["id"]:02d}</span>{html.escape(i["title"])}</a>')
 nav.append('</div>')
articles=[]
for f in files:
 key=ids[f.resolve()];rel=f.relative_to(ROOT).as_posix()
 articles.append(f'<article id="{key}" {"" if key=="home" else "hidden"}><div class="doc-meta">ATLAS TUTORIALS · 中文全集 <a href="{html.escape(rel)}">Markdown 源文件 ↗</a></div>'+render(f)+'</article>')
css=r'''
:root{--ink:#19302c;--muted:#5d716b;--accent:#177052;--line:#dce5df;--paper:#fff;--bg:#f3f6f2;--sidebar:#112d26}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",sans-serif;font-size:16px;line-height:1.85}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}[hidden]{display:none!important}
aside{position:fixed;inset:0 auto 0 0;width:330px;background:var(--sidebar);color:#d6e8df;display:flex;flex-direction:column;padding:25px 18px;z-index:5}
.brand{padding:0 10px}.brand strong{display:block;font-size:25px;letter-spacing:2px;color:#fff}.brand small{color:#a9c9ba}.search-box{margin:20px 5px 12px}input{width:100%;padding:12px 14px;border:1px solid #628575;border-radius:8px;background:#244438;color:#fff;font-size:14px}input::placeholder{color:#bbd1c6}input:focus{outline:2px solid #92d5ae}
#count{font-size:12px;color:#b4c9bd;padding:0 8px 8px}nav{overflow:auto;padding:0 3px 20px}nav a{display:flex;gap:11px;padding:8px 9px;color:#d6e8df;line-height:1.6;font-size:13px;border-radius:6px;margin:2px 0}nav a.active{background:#35634c;color:#fff}nav a:hover{background:#284e3d;text-decoration:none}nav a span{color:#9fbbaa;font-size:12px;min-width:22px;padding-top:2px}nav h3{font-size:11px;letter-spacing:2px;color:#93b29f;margin:21px 9px 6px}.home-link{font-size:14px}
main{margin-left:330px;padding:34px 5vw 70px;max-width:1510px}header{display:flex;justify-content:space-between;align-items:center;margin:0 auto 22px;max-width:920px;color:var(--muted);font-size:12px}.badge{padding:4px 12px;border:1px solid #c8d8cc;border-radius:20px;background:#e9f1e8}
article{max-width:920px;margin:0 auto;background:var(--paper);padding:45px 54px 60px;border:1px solid var(--line);border-radius:12px;box-shadow:0 8px 35px #19302c05}.doc-meta{font-size:10px;letter-spacing:1.2px;color:#6b8377;display:flex;gap:18px;justify-content:space-between;margin-bottom:25px}.doc-meta a{letter-spacing:0;font-size:11px}
h1{font-size:31px;line-height:1.5;letter-spacing:-.5px;margin:0 0 24px}h2{font-size:21px;line-height:1.5;margin:35px 0 13px;border-top:1px solid #eef2ed;padding-top:24px}h3{font-size:18px}p{margin:15px 0}strong{font-weight:650}blockquote{margin:20px 0;padding:5px 19px;background:#eff7ef;border-left:3px solid #4e9875;border-radius:0 7px 7px 0}blockquote p{margin:10px 0}
pre{position:relative;background:#152c26;color:#e3f4e9;border-radius:9px;padding:42px 20px 20px;overflow:auto;font-size:12.5px;line-height:1.75}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}p code,td code,li code{background:#f0f5ef;padding:2px 5px;border-radius:4px;font-size:.85em;overflow-wrap:anywhere}pre code{background:none}.copy{position:absolute;right:10px;top:9px;color:#dcf5e4;background:#2c5140;border:1px solid #587d67;padding:3px 12px;border-radius:5px;cursor:pointer;font-size:11px}table{border-collapse:collapse;width:100%;font-size:13px;margin:20px 0;display:block;overflow-x:auto}th,td{padding:12px 13px;border:1px solid var(--line);text-align:left;min-width:120px;vertical-align:top}th{background:#eef4ed}td:last-child{width:100%}ul,ol{padding-left:23px}.page-nav{display:flex;max-width:920px;margin:24px auto;justify-content:space-between;gap:20px}.page-nav a{font-size:12px;max-width:45%}.mobile-toggle{display:none}footer{max-width:920px;margin:32px auto;font-size:11px;color:var(--muted)}
@media(max-width:1000px){aside{width:280px}main{margin-left:280px;padding:26px 25px}article{padding:30px}h1{font-size:26px}}
@media(max-width:730px){aside{display:none;width:min(90vw,350px)}body.menu-open aside{display:flex}main{margin:0;padding:65px 14px 30px}article{padding:24px 20px;border-radius:8px}h1{font-size:23px}.doc-meta{font-size:9px;gap:8px}.mobile-toggle{display:block;position:fixed;top:14px;right:14px;z-index:8;background:#173d2c;color:white;border:0;padding:10px 16px;border-radius:7px}header{gap:10px;font-size:10px}pre{font-size:11px;padding-left:14px}}
@media print{aside,header,.copy,.page-nav,footer,.mobile-toggle{display:none!important}main{margin:0;padding:0}article{border:0;box-shadow:none;padding:10px}pre{white-space:pre-wrap;background:#f5f5f5;color:#111}}
'''
js=r'''
const all=Array.from(document.querySelectorAll('article'));const links=Array.from(document.querySelectorAll('.lesson-link'));const search=document.querySelector('#search');
const texts=new Map(all.map(a=>[a.id,a.textContent.toLowerCase()]));
function activate(){let key=decodeURIComponent(location.hash.slice(1)||'home');if(!document.getElementById(key))key='home';for(const a of all)a.hidden=a.id!==key;for(const a of document.querySelectorAll('nav a'))a.classList.toggle('active',a.getAttribute('href')==='#'+key);const index=links.findIndex(a=>a.dataset.target===key);const prev=document.querySelector('#prev'),next=document.querySelector('#next');prev.hidden=index<=0;next.hidden=index<0||index>=links.length-1;if(index>0){prev.href=links[index-1].href;prev.textContent='← '+links[index-1].textContent;}if(index>=0&&index<links.length-1){next.href=links[index+1].href;next.textContent=links[index+1].textContent+' →';}document.body.classList.remove('menu-open');window.scrollTo(0,0);const h=document.querySelector('article:not([hidden]) h1');document.title=(h?h.textContent:'Atlas')+' · 教程全集';}
search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();let n=0;for(const a of links){a.hidden=!!q&&!texts.get(a.dataset.target).includes(q);if(!a.hidden)n++;}for(const g of document.querySelectorAll('.nav-group'))g.hidden=!Array.from(g.querySelectorAll('.lesson-link')).some(a=>!a.hidden);document.querySelector('#count').textContent=q?`匹配 ${n} / 48 篇`:'48 篇完整教程 · 支持全文检索';});
for(const pre of document.querySelectorAll('pre')){const code=pre.querySelector('code');if(!code)continue;const b=document.createElement('button');b.className='copy';b.type='button';b.textContent='复制';b.addEventListener('click',async()=>{try{if(navigator.clipboard){await navigator.clipboard.writeText(code.textContent);}else{const t=document.createElement('textarea');t.value=code.textContent;document.body.append(t);t.select();document.execCommand('copy');t.remove();}b.textContent='已复制';setTimeout(()=>b.textContent='复制',1300);}catch{b.textContent='请手动选中复制';}});pre.append(b);}
document.querySelector('.mobile-toggle').addEventListener('click',()=>document.body.classList.toggle('menu-open'));window.addEventListener('hashchange',activate);activate();
'''
page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Atlas 教程全集</title><meta name="theme-color" content="#112d26"><meta name="description" content="48 篇 Atlas 多模态 Agent 中文教程，覆盖 CLI / Skill / MCP / API 接入、图片、视频、声音、后处理、自动化与排错。"><link rel="canonical" href="https://majiayu000.github.io/atlas-tutorials/"><meta property="og:type" content="website"><meta property="og:title" content="Atlas 多模态 Agent 教程全集"><meta property="og:description" content="48 篇 Atlas 多模态 Agent 中文教程，覆盖 CLI / Skill / MCP / API 接入、图片、视频、声音、后处理、自动化与排错。"><meta property="og:url" content="https://majiayu000.github.io/atlas-tutorials/"><meta property="og:image" content="https://majiayu000.github.io/atlas-tutorials/social-card.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Atlas 多模态 Agent 教程全集 · 公开页面预览"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Atlas 多模态 Agent 教程全集"><meta name="twitter:description" content="48 篇 Atlas 多模态 Agent 中文教程，覆盖 CLI / Skill / MCP / API 接入、图片、视频、声音、后处理、自动化与排错。"><meta name="twitter:image" content="https://majiayu000.github.io/atlas-tutorials/social-card.png"><style>'+css+'</style></head><body><button class="mobile-toggle">目录</button><aside><div class="brand"><strong>ATLAS</strong><small>多模态 Agent · 教程全集</small></div><div class="search-box"><input id="search" aria-label="搜索教程全文" placeholder="搜索场景、命令、排错…"></div><div id="count">48 篇完整教程 · 支持全文检索</div><nav>'+''.join(nav)+'</nav></aside><main><header><span>从接入到成片，从脚本到生态</span><span class="badge">离线可读 · 2026.09.20</span></header>'+''.join(articles)+'<div class="page-nav"><a id="prev" hidden></a><a id="next" hidden></a></div><footer>文稿与离线验证已完成；真实账户、付费模型与宿主联调需另行确认。无外部字体、无追踪脚本。</footer></main><script>'+js+'</script></body></html>'
(ROOT/'index.html').write_text(page,encoding='utf-8')
guide_dir=ROOT/'guides'
guide_dir.mkdir(exist_ok=True)
base='https://majiayu000.github.io/atlas-tutorials/'
guide_links=' · '.join(f'<a href="{filename}">{html.escape(title)}</a>' for filename,title in guides.values())
for source,(filename,title) in guides.items():
 head=page.split('<style>')[0]
 head=re.sub(r'<title>.*?</title>', '<title>'+html.escape(title)+'</title>', head)
 head=re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description|og:title|twitter:title)" content=")[^"]*', lambda m:m.group(1)+html.escape(title), head)
 head=head.replace(base+'"',base+'guides/'+filename+'"')
 body='<main><header><a href="../index.html">← 全部 48 篇与离线阅读器</a><a href="https://github.com/majiayu000/atlas-tutorials">项目与反馈</a></header><article>'+render(source,standalone=True)+'</article><footer><nav>'+guide_links+'</nav><p>原文与版本依据：<a href="../SOURCES.md">资料来源</a> · <a href="../verification/REPORT.md">离线验证记录</a> · <a href="../'+source.relative_to(ROOT).as_posix()+'">Markdown 原文</a></p></footer></main>'
 (guide_dir/filename).write_text(head+'<style>'+css+'main{margin:0 auto}footer nav a{display:inline;color:var(--accent);font-size:inherit}</style></head><body>'+body+'</body></html>',encoding='utf-8')
urls=[base,*[base+'guides/'+filename for filename,_ in guides.values()]]
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+u+'</loc></url>\n' for u in urls)+'</urlset>\n',encoding='utf-8')
print(f'Built {len(CAT)} tutorials + supporting docs; {len(page.encode())} bytes')
