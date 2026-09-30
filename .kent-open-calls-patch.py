from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'Pattern not found: {label}')
    s=s.replace(old,new,1)

old='''  if(sig){
    emojiEl.textContent=sig.emoji||"";
    signalBtn.disabled=true;
    kentBtn.disabled=uid===sig.senderUid || myTeam!==sig.team;
    contraBtn.disabled=myTeam===sig.team;
    return;
  }
  signalBtn.disabled=false;
  kentBtn.disabled=true;
  contraBtn.disabled=true;
'''
new='''  signalBtn.disabled=false;
  kentBtn.disabled=false;
  contraBtn.disabled=false;
  if(sig){
    emojiEl.textContent=sig.emoji||"";
    return;
  }
'''
rep(old,new,'buttons always active')

rep('''    const current=room.game?.signal;
    if(current && !current.resolved && Number(current.expiresAt)>now) return;
    const team=playerTeam(caller);''','''    const team=playerTeam(caller);''','allow signal interruption')

start=s.index('async function resolveCall(type){')
end=s.index('\nasync function nextRound(){',start)
new_func='''async function resolveCall(type){
  const now=serverNow();
  await runTransaction(ref(db,`${ROOT}/${roomCode}`),room=>{
    if(!room || room.state!=="playing") return;
    const caller=room.players?.[uid];
    if(!caller) return;
    const callerTeam=playerTeam(caller);
    const allPlayers=Object.entries(room.players||{}).map(([id,p])=>({id,...p}));
    let success=false, text="";

    if(type==="kent"){
      success=allPlayers.some(p=>p.id!==uid && playerTeam(p)===callerTeam && hasFour(room.game.hands?.[p.id]));
      text=success ? `${caller.name} správně hlásí KENT` : `${caller.name} hlásí KENT chybně`;
    }else{
      success=allPlayers.some(p=>playerTeam(p)!==callerTeam && hasFour(room.game.hands?.[p.id]));
      text=success ? `${caller.name} správně hlásí KONTRA` : `${caller.name} hlásí KONTRA chybně`;
    }

    room.game.score=room.game.score||emptyScore(maxPlayers(room));
    if(success) room.game.score[callerTeam]=(room.game.score[callerTeam]||0)+1;
    else room.game.score[callerTeam]=Math.max(0,(room.game.score[callerTeam]||0)-1);

    if(room.game?.signal){
      room.game.signal.resolved=true;
      room.game.signal.resolvedBy=uid;
      room.game.signal.response=type;
      room.game.signal.resolvedAt=now;
    }

    room.game.lastEvent={
      title:type==="kent"?"KENT!":"KONTRA!",
      text,
      winnerTeam:success?callerTeam:null,
      penaltyTeam:success?null:callerTeam,
      by:uid,
      time:now
    };
    room.state=Object.values(room.game.score).some(points=>Number(points)>=WIN_SCORE)?"finished":"roundEnd";
    room.updatedAt=now;
    return room;
  });
}
'''
s=s[:start]+new_func+s[end:]

p.write_text(s,encoding='utf-8')
