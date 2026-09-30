from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'Pattern not found: {label}')
    s=s.replace(old,new,1)

rep('const DECOY_VISIBLE_MS = 1750;\n','', 'remove emoji gap constant')

rep('''.signal-corner{position:fixed;z-index:4;top:max(76px,calc(env(safe-area-inset-top) + 64px));right:14px;width:64px;height:64px;border-radius:20px;border:1px solid rgba(255,255,255,.2);background:rgba(5,43,31,.82);backdrop-filter:blur(8px);display:grid;place-items:center;box-shadow:0 12px 30px rgba(0,0,0,.28);transition:opacity .12s,transform .12s;pointer-events:none}\n.signal-corner.hidden{display:none!important}\n.signal-corner .signal-emoji{font-size:38px;line-height:1}\n.signal-corner.real{outline:2px solid rgba(241,196,77,.8);transform:scale(1.05)}\n@media(max-width:430px){.create-options{grid-template-columns:1fr}.emoji-choice{width:32px;height:32px;font-size:19px}.signal-corner{width:58px;height:58px;border-radius:18px;top:max(72px,calc(env(safe-area-inset-top) + 60px));right:10px}.signal-corner .signal-emoji{font-size:34px}}''','''.contra-signal{display:grid;grid-template-columns:1fr;gap:6px;min-width:0}\n.contra-signal.remote{grid-template-columns:minmax(0,1fr) 52px}\n.contra-signal .btn{width:100%;min-width:0}\n.signal-corner{width:52px;min-height:54px;display:grid;place-items:center;pointer-events:none}\n.signal-corner.hidden{display:none!important}\n.signal-corner .signal-emoji{font-size:36px;line-height:1}\n@media(max-width:430px){.create-options{grid-template-columns:1fr}.emoji-choice{width:32px;height:32px;font-size:19px}.contra-signal.remote{grid-template-columns:minmax(0,1fr) 48px}.signal-corner{width:48px;min-height:49px}.signal-corner .signal-emoji{font-size:32px}}''','signal layout css')

rep('''        <button class="btn" id="contraBtn">KONTRA</button>\n      </div>''','''        <div class="contra-signal" id="contraSignalWrap">\n          <button class="btn" id="contraBtn">KONTRA</button>\n          <div class="signal-corner hidden" id="signalCorner"><span class="signal-emoji" id="signalEmoji"></span></div>\n        </div>\n      </div>''','move signal next to contra')

rep('''\n<div class="signal-corner hidden" id="signalCorner"><span class="signal-emoji" id="signalEmoji"></span></div>\n''','\n','remove floating signal')

old_func='''function renderSignalCorner(){\n  const corner=$("signalCorner"), emojiEl=$("signalEmoji");\n  if(!corner || !roomData?.remoteMode || roomData.state!=="playing"){\n    corner?.classList.add("hidden");\n    return;\n  }\n  const now=serverNow();\n  const sig=activeRemoteSignal(roomData,now);\n  const myTeam=playerTeam(me());\n  const signalBtn=$("signalBtn"), kentBtn=$("kentBtn"), contraBtn=$("contraBtn");\n  if(sig){\n    corner.classList.remove("hidden");\n    corner.classList.add("real");\n    emojiEl.textContent=sig.emoji||"";\n    signalBtn.disabled=true;\n    kentBtn.disabled=uid===sig.senderUid || myTeam!==sig.team;\n    contraBtn.disabled=myTeam===sig.team;\n    return;\n  }\n  corner.classList.remove("real");\n  signalBtn.disabled=false;\n  kentBtn.disabled=true;\n  contraBtn.disabled=true;\n  const phase=((now%DECOY_SLOT_MS)+DECOY_SLOT_MS)%DECOY_SLOT_MS;\n  if(phase>DECOY_VISIBLE_MS){corner.classList.add("hidden");return}\n  const excluded=new Set(Object.values(roomData.teamEmojis||{}).filter(Boolean));\n  const pool=DECOY_EMOJIS.filter(e=>!excluded.has(e));\n  const slot=Math.floor(now/DECOY_SLOT_MS);\n  const idx=pool.length?hashString(`${roomCode}:${slot}`)%pool.length:0;\n  emojiEl.textContent=pool[idx]||"🙂";\n  corner.classList.remove("hidden");\n}\n'''
new_func='''function renderSignalCorner(){\n  const corner=$("signalCorner"), emojiEl=$("signalEmoji");\n  if(!corner || !roomData?.remoteMode || roomData.state!=="playing"){\n    corner?.classList.add("hidden");\n    return;\n  }\n  const now=serverNow();\n  const sig=activeRemoteSignal(roomData,now);\n  const myTeam=playerTeam(me());\n  const signalBtn=$("signalBtn"), kentBtn=$("kentBtn"), contraBtn=$("contraBtn");\n  corner.classList.remove("hidden");\n  if(sig){\n    emojiEl.textContent=sig.emoji||"";\n    signalBtn.disabled=true;\n    kentBtn.disabled=uid===sig.senderUid || myTeam!==sig.team;\n    contraBtn.disabled=myTeam===sig.team;\n    return;\n  }\n  signalBtn.disabled=false;\n  kentBtn.disabled=true;\n  contraBtn.disabled=true;\n  const excluded=new Set(Object.values(roomData.teamEmojis||{}).filter(Boolean));\n  const pool=DECOY_EMOJIS.filter(e=>!excluded.has(e));\n  const slot=Math.floor(now/DECOY_SLOT_MS);\n  const idx=pool.length?hashString(`${roomCode}:${slot}`)%pool.length:0;\n  emojiEl.textContent=pool[idx]||"🙂";\n}\n'''
rep(old_func,new_func,'continuous signal rendering')

rep('''  const lastMove=g.lastMove;\n  const moveAge=lastMove?.at ? Date.now()-lastMove.at : Infinity;''','''  const lastMove=g.lastMove;\n  const moveAge=lastMove?.at ? serverNow()-lastMove.at : Infinity;''','shared move timing display')

rep('''  const remote=!!roomData.remoteMode;\n  const signalBtn=$("signalBtn");\n  signalBtn.classList.toggle("hidden",!remote);''','''  const remote=!!roomData.remoteMode;\n  const signalBtn=$("signalBtn");\n  $("contraSignalWrap")?.classList.toggle("remote",remote);\n  signalBtn.classList.toggle("hidden",!remote);''','remote signal layout toggle')

rep('''async function swapCards(){\n  const hi=selectedHand, ti=selectedTable;\n  selectedHand=selectedTable=null;\n  await runTransaction(ref(db,`${ROOT}/${roomCode}`),room=>{''','''async function swapCards(){\n  const hi=selectedHand, ti=selectedTable;\n  const moveTime=serverNow();\n  selectedHand=selectedTable=null;\n  await runTransaction(ref(db,`${ROOT}/${roomCode}`),room=>{''','shared move timestamp start')

rep('''    room.game.turn=(room.game.turn||0)+1;\n    const now=Date.now();\n    room.game.lastMove={''','''    room.game.turn=(room.game.turn||0)+1;\n    const now=moveTime;\n    room.game.lastMove={''','shared move timestamp')

p.write_text(s,encoding='utf-8')
