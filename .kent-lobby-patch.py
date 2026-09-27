from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'Pattern not found: {label}')
    s=s.replace(old,new,1)

rep('''      <input class="field" id="nameInput" maxlength="16" placeholder="Tvoje jméno" autocomplete="nickname">
      <div class="create-options">
        <div class="option-box">
          <span class="option-title">Hráči</span>
          <select class="select" id="playerCountInput" aria-label="Počet hráčů">
            <option value="4">4</option>
            <option value="6">6</option>
            <option value="8">8</option>
            <option value="10">10</option>
          </select>
        </div>
        <label class="option-box toggle-box"><input type="checkbox" id="remoteInput"><span>Hrajeme na dálku</span></label>
      </div>
      <button class="btn primary" id="createBtn">Založit hru</button>''','''      <input class="field" id="nameInput" maxlength="16" placeholder="Tvoje jméno" autocomplete="nickname">
      <div style="height:10px"></div>
      <button class="btn primary" id="createBtn">Založit hru</button>''','home settings')

rep('''        <div class="room-meta" id="roomMeta"></div>
        <button class="btn" id="shareBtn" style="min-height:44px;margin-top:8px">Sdílet odkaz</button>
      </div>
      <div class="players" id="playersList"></div>''','''        <div class="room-meta" id="roomMeta"></div>
        <button class="btn" id="shareBtn" style="min-height:44px;margin-top:8px">Sdílet odkaz</button>
      </div>
      <div class="create-options hidden" id="lobbySettings">
        <div class="option-box">
          <span class="option-title">Hráči</span>
          <select class="select" id="lobbyPlayerCount" aria-label="Počet hráčů">
            <option value="4">4</option>
            <option value="6">6</option>
            <option value="8">8</option>
            <option value="10">10</option>
          </select>
        </div>
        <label class="option-box toggle-box"><input type="checkbox" id="lobbyRemote"><span>Hrajeme na dálku</span></label>
      </div>
      <div class="players" id="playersList"></div>''','lobby settings')

rep('''const nameInput=$("nameInput"), roomInput=$("roomInput");
const playerCountInput=$("playerCountInput"), remoteInput=$("remoteInput");
const startBtn=$("startBtn"), newTableBtn=$("newTableBtn");''','''const nameInput=$("nameInput"), roomInput=$("roomInput");
const lobbyPlayerCount=$("lobbyPlayerCount"), lobbyRemote=$("lobbyRemote"), lobbySettings=$("lobbySettings");
const startBtn=$("startBtn"), newTableBtn=$("newTableBtn");''','element refs')

rep('''  const limit=maxPlayers();
  $("roomMeta").textContent=`${limit} hráčů · ${roomData.remoteMode?"na dálku":"u jednoho stolu"}`;
  playersList.innerHTML="";''','''  const limit=maxPlayers();
  $("roomMeta").textContent=`${limit} hráčů · ${roomData.remoteMode?"na dálku":"u jednoho stolu"}`;
  lobbySettings.classList.toggle("hidden",!amHost());
  lobbyPlayerCount.value=String(limit);
  lobbyRemote.checked=!!roomData.remoteMode;
  const joinedCount=playersArray().length;
  for(const option of lobbyPlayerCount.options) option.disabled=Number(option.value)<joinedCount;
  playersList.innerHTML="";''','render lobby controls')

rep('''  const name=normalizeName();
  const limit=Number(playerCountInput.value)||4;
  const remoteMode=!!remoteInput.checked;
  let code;''','''  const name=normalizeName();
  const limit=4;
  const remoteMode=false;
  let code;''','create defaults')

marker='async function removePlayer(playerId){'
insert='''async function setLobbyPlayerCount(rawLimit){
  const limit=Number(rawLimit);
  if(!amHost() || roomData?.state!=="lobby" || ![4,6,8,10].includes(limit)) return;
  if(playersArray().length>limit){
    toast(`V místnosti už je ${playersArray().length} hráčů`);
    renderLobby();
    return;
  }
  await runTransaction(ref(db,`${ROOT}/${roomCode}`),room=>{
    if(!room || room.state!=="lobby" || room.hostUid!==uid) return;
    const entries=Object.entries(room.players||{}).sort((a,b)=>(a[1]?.seat??99)-(b[1]?.seat??99));
    if(entries.length>limit) return;
    const players={};
    entries.forEach(([id,p],seat)=>{
      players[id]={...p,seat,team:teamOfSeat(seat)};
    });
    room.players=players;
    room.maxPlayers=limit;
    const allowedTeams=Array.from({length:limit/2},(_,i)=>String.fromCharCode(65+i));
    room.teamEmojis=Object.fromEntries(Object.entries(room.teamEmojis||{}).filter(([team])=>allowedTeams.includes(team)));
    room.game=room.game||{};
    room.game.score=emptyScore(limit);
    room.updatedAt=Date.now();
    return room;
  });
}

async function setLobbyRemoteMode(enabled){
  if(!amHost() || roomData?.state!=="lobby") return;
  await update(ref(db,`${ROOT}/${roomCode}`),{
    remoteMode:!!enabled,
    updatedAt:Date.now()
  });
}

'''
if marker not in s:
    raise SystemExit('Pattern not found: removePlayer marker')
s=s.replace(marker,insert+marker,1)

rep('''$("nextRoundBtn").onclick=nextRound;
$("newGameBtn").onclick=()=>startGame(true);

$("shareBtn").onclick=async()=>{
  const u=new URL(location.href); u.searchParams.set("room",roomCode);
  try{
    if(navigator.share) await navigator.share({title:"Kent",text:`Kent · místnost ${roomCode}`,url:u.href});
    else{await navigator.clipboard.writeText(u.href);toast("Odkaz zkopírován");}
  }catch{}
};''','''$("nextRoundBtn").onclick=nextRound;
$("newGameBtn").onclick=()=>startGame(true);
lobbyPlayerCount.onchange=()=>setLobbyPlayerCount(lobbyPlayerCount.value);
lobbyRemote.onchange=()=>setLobbyRemoteMode(lobbyRemote.checked);

$("shareBtn").onclick=async()=>{
  const u=new URL("https://bernio.cz/kent/");
  u.searchParams.set("room",roomCode);
  try{
    if(navigator.share) await navigator.share({url:u.href});
    else{await navigator.clipboard.writeText(u.href);toast("Odkaz zkopírován");}
  }catch{}
};''','share and settings handlers')

rep('''        if(pendingRoomFromUrl){
          pendingRoomFromUrl="";
          joinRoom(roomInput.value);
        }
''','', 'disable auto join')

p.write_text(s,encoding='utf-8')
