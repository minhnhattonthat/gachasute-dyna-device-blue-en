-- Debug warp for Gachasute! Dyna Device Blue. Boots cold, fills the profile form, starts a new game and lands on
-- the scene named by SCENE (tools/debug/scenes.tsv). RE notes: docs/re/debug.md.
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='intro'" --frames 900 --sheet
-- Globals (all optional except SCENE):
--   SCENES  path of the scene list (default: ../debug/scenes.tsv, relative to tools/mesen, Mesen's working folder)
--   HOLD    frames to keep running after the scene is reached (default: the scene's hold column, else 300)
--   MASHA   1 = press A every 40 frames after arrival (click through dialogue)
--   GOD     reserved (battles): not wired yet
--   FINISH  1 = stop the run once the hold shot is taken; WARP_STATE = path: save a state there, then stop
--   (tools/debug/regen.py sets both)
-- Log lines: "WARP <stage>" at each stage, "ARRIVED <scene> f<frame>" when the scene is up, "SCRIPT <n>" whenever
-- the game starts an event script (with the caller's PC).

local SCRIPT_START = 0x0801A9D4  -- start_script(r0 = file 2, r1 = script index); docs/re/debug.md
local FORM_INPUT   = 0x0803C6B4  -- profile form: key read, runs only while the form is idle (no popup)
local SCR          = 0x02001C60  -- running script: +0 pc, +4 start, +0x10 current opcode (0 = none)
local TEXT_DRAW    = 0x08013488  -- message text drawer, r0 = SJIS string (called by script op 2)

local EVENT_PICK   = 0x0801E868  -- picks the story event at each room load from the flags (returns -1 = none)
local FLAGS        = 0x0200A300  -- story flags: 2 bits each, flag n in byte n>>2 at bit (n&3)*2; event e uses flag e
local DAYS         = 0x0200A7A4  -- days elapsed (u8); events need a minimum day count
local ROOM         = 0x02001C54  -- current room (i16): 0 = Dyna City sector map, 15 = reception
local EVENT_SCRIPTS = 0x080CED94 -- i16 per event: the script the room load starts for it
local DATE_PROMPT  = 0x08040C28  -- boot date prompt: loads its string きょうの ひづけを...

local MEM = emu.memType.gbaMemory
local function r16(a) return emu.read16(a, MEM) end
local function set_flag(n, v)
  local a = FLAGS + (n >> 2)
  local sh = (n & 3) * 2
  local b = emu.read(a, MEM)
  emu.write(a, (b & ~(3 << sh) & 0xFF) | ((v & 3) << sh), MEM)
end
local function get_flag(n) return (emu.read(FLAGS + (n >> 2), MEM) >> ((n & 3) * 2)) & 3 end

-- scene list: name, kind, arg, hold, note (tab separated, '#' comments)
local scenes = {}
do
  local path = SCENES or "../debug/scenes.tsv"
  for line in io.lines(path) do
    if not line:match("^%s*#") and line:match("%S") then
      local f = {}
      for col in (line .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = col end
      if f[1] ~= "name" then
        scenes[f[1]] = { name = f[1], kind = f[2], arg = f[3], hold = tonumber(f[4]), note = f[5] }
      end
    end
  end
end
local scene = scenes[SCENE or ""]
if not scene then L.fail("unknown SCENE " .. tostring(SCENE)) return end
local hold = tonumber(HOLD) or scene.hold or 300

local TUT_ROUTE = (SCENES and SCENES:gsub("[^/\\]+$", "") or "../debug/") .. "tutorial_route.txt"
local TUT_MASH = 2997  -- frames of A-mashing from script 1's start before the recorded tutorial route begins
local tutStart = 0
local tutRouteT = nil  -- tutorial frame the recorded route starts (set from the script-10 nag)
local arriveAfterRoute = false  -- arrive when the queued input route has played out
local stage, stageFrame = "boot", 0
local arrived = nil
local function set_stage(s)
  stage, stageFrame = s, L.frame
  L.log(string.format("WARP %s f%d", s, L.frame))
end
local function arrive()
  if arrived then return end
  arrived = L.frame
  L.log(string.format("ARRIVED %s f%d", scene.name, L.frame))
  L.shot("arrived.png")
end

-- seq: list of {spec, frames}
local function play(seq)
  for _, s in ipairs(seq) do L.press(s[1], s[2]) end
end
local function parse_route(str)
  local seq = {}
  for step in str:gmatch("[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    seq[#seq + 1] = { spec, tonumber(n) }
  end
  return seq
end

-- Profile form: name あああ, nickname あああ, gender as is, skip the postal-code keyboard, down to おわる, A.
local FORM = parse_route("10 -;6 a;80 -;6 a;40 -;6 a;40 -;6 a;40 -;6 start;80 -;6 a;80 -;6 a;40 -;6 a;40 -;" ..
  "6 a;40 -;6 start;100 -;6 a;100 -;6 b;60 -;6 down;40 -;6 down;40 -;6 down;40 -;6 down;40 -;6 down;40 -;" ..
  "6 down;40 -;6 a;60 -")

local formSeen, scriptCount, formLast = false, 0, -1
L.on_exec(FORM_INPUT, FORM_INPUT, function()
  formLast = L.frame
  if not formSeen then
    formSeen = true
    if scene.kind == "boot" and scene.arg == "form" then set_stage("done"); arrive(); return end
    if scene.kind == "boot" and scene.arg == "keyboard" then
      set_stage("done"); play(parse_route("10 -;6 a;80 -")); arrive(); return
    end
    set_stage("form")
    play(FORM)
  end
end)

-- kinds "event" and "field": before the game's first event pick, set flag 1 = 3 (intro done), every other story
-- flag to 0, flag E = 3 (event E pending; "event" only), extra "flag=value" pokes from the arg, and a high day
-- count. The new game then skips the tutorial, and the pick starts event E's script as soon as the player is in
-- the room it needs (reception 15 at once; city 0 after walking out of the south door).
-- arg: "event" = "E[ flag=value ...]"; "field" = an input route played once the player stands in the city.
local flagsSet = false
L.on_exec(EVENT_PICK, EVENT_PICK, function()
  if (scene.kind == "event" or scene.kind == "field") and not flagsSet then
    flagsSet = true
    for n = 2, 95 do set_flag(n, 0) end
    set_flag(1, 3)
    if scene.kind == "event" then
      set_flag(tonumber(scene.arg:match("^%s*(%d+)")), 3)
      for k, v in scene.arg:gmatch("(%d+)=(%d+)") do set_flag(tonumber(k), tonumber(v)) end
    end
    if scene.kind == "event" then emu.write(DAYS, 99, MEM) end
    set_stage("walk")
  end
end)

-- kind "mode": arg "N[ route]". The top-level dispatcher (0x08004DB8) picks the task for game mode N
-- (u32 0x03001AD0, jump table 0x08004DF0, modes 1..50; docs/re/debug.md). Its first pick (logo, mode 29) is replaced
-- by mode N at a cold boot, so the screen starts with no profile, party or items. Mode 50 = the leftover
-- "AGB SYSTEM DEBUG MENU"; the route then picks its entries.
local MODE_VAR, MODE_PICK = 0x03001AD0, 0x08004DD4
local modeForced = false
L.on_exec(MODE_PICK, MODE_PICK, function()
  if scene.kind ~= "mode" or modeForced then return end
  modeForced = true
  local want = tonumber(scene.arg:match("^%s*(%d+)"))
  local route = scene.arg:match("^%s*%d+%s+(.+)$")
  emu.write32(MODE_VAR, want, MEM)
  emu.write(0x03001830 + want, 1, MEM)
  emu.setState({ ["cpu.r0"] = want })
  set_stage("done")
  play(parse_route("1 -;" .. (route or "60 -")))
  arriveAfterRoute = true
end)

-- kind "resume": arg "flag=value ...[ score=N][ | route]". The field init (0x08055D84) branches on an entry code in
-- r4 (57 = new game; 59 and others = continue). The continue handler 0x080522D4 restarts the story script in
-- progress from the flags (chain of flag tests, docs/re/debug.md: e.g. flag 75 == 1 -> script 152, flag 95 == 3 ->
-- epilogue 153, or 155 when the completion score 0x0801A6C4 is above 99; nothing set -> 154). Here the new game's
-- entry code becomes 59, every story flag is cleared, flag 1 = 3, the pokes are applied and, with score=N, the
-- score the epilogue test reads (r0 at 0x0805266E) is replaced.
local RESUME_FIELD, RESUME_DISPATCH, RESUME_SCORE = 0x08055D84, 0x080522D4, 0x0805266E
local resumeSet = false
L.on_exec(RESUME_SCORE, RESUME_SCORE, function()
  local sc = scene.kind == "resume" and tonumber(scene.arg:match("score=(%d+)"))
  if sc then emu.setState({ ["cpu.r0"] = sc }) end
end)
L.on_exec(RESUME_FIELD, RESUME_FIELD, function()
  if scene.kind ~= "resume" or resumeSet then return end
  L.log(string.format("FIELDINIT entry=%d f%d", emu.getState()["cpu.r4"], L.frame))
  resumeSet = true
  emu.setState({ ["cpu.r4"] = 59 })
  for n = 2, 127 do set_flag(n, 0) end
  set_flag(1, 3)
  local pokes = scene.arg:match("^([^|]*)")
  for k, v in pokes:gmatch("(%d+)=(%d+)") do set_flag(tonumber(k), tonumber(v)) end
  emu.write(DAYS, 99, MEM)
  set_stage("resume")
end)
L.on_exec(RESUME_DISPATCH, RESUME_DISPATCH, function()
  if scene.kind == "resume" then L.log(string.format("RESUME dispatch f%d", L.frame)) end
end)

-- kind "dmode": arg "N[ route]". Mode N entered with real game data: the tutorial plays out as for "menu" (2 Dynas,
-- 4300 bits, an item shop sector), then system > おわる > yes quits the field, and the game's next set_mode call
-- (0x08002C1C, r0 = 2 after a quit) gets mode N instead. Party, items and money stay in RAM.
local SET_MODE = 0x08002C1C
local QUIT_ROUTE = "6 b;60 -;6 right;30 -;6 a;40 -;6 down;20 -;6 down;20 -;6 a;90 -;6 a;60 -"
L.on_exec(SET_MODE, SET_MODE, function()
  if scene.kind ~= "dmode" or stage ~= "dquit" then return end
  local want = tonumber(scene.arg:match("^%s*(%d+)"))
  local route = scene.arg:match("^%s*%d+%s+(.+)$")
  L.log(string.format("SETMODE %d -> %d f%d", emu.getState()["cpu.r0"], want, L.frame))
  emu.setState({ ["cpu.r0"] = want, ["cpu.r1"] = 1 })
  set_stage("done")
  play(parse_route("1 -;" .. (route or "120 -")))
  arriveAfterRoute = true
end)

local dateSeen = false
L.on_exec(DATE_PROMPT, DATE_PROMPT, function()
  if not dateSeen and scene.kind == "boot" and scene.arg == "date" then
    dateSeen = true
    set_stage("done")
    arrive()
  end
end)

L.on_exec(SCRIPT_START, SCRIPT_START, function()
  local s = emu.getState()
  local idx = s["cpu.r1"]
  scriptCount = scriptCount + 1
  if scene.kind == "field" and stage == "walk" and idx >= 780 and idx <= 795 then
    -- a visiting challenger (scripts 780-795, yes/no battle offer) would block the field: run the empty script 331
    emu.setState({ ["cpu.r1"] = 331 })
    L.log(string.format("SCRIPT %d -> 331 (visitor suppressed) f%d", idx, L.frame))
    return
  end
  if scene.kind == "script" and scriptCount == 1 then
    -- arg: "N[ route]": script N, then (optional) an input route played from the script's start
    local want = tonumber(scene.arg:match("^%s*(%d+)"))
    local route = scene.arg:match("^%s*%d+%s+(.+)$")
    if route then play(parse_route("1 -;" .. route)); arriveAfterRoute = true end
    emu.setState({ ["cpu.r1"] = want })
    L.log(string.format("SCRIPT %d -> %d (hijacked) lr=%08X f%d", idx, want, s["cpu.r14"] or 0, L.frame))
    idx = want
  else
    L.log(string.format("SCRIPT %d lr=%08X room=%d f%d", idx, s["cpu.r14"] or 0, r16(ROOM), L.frame))
  end
  if stage == "tutorial" and idx == 10 and not tutRouteT and L.frame - tutStart >= TUT_MASH - 400 then
    -- script 10 is the "press A at the Gachasute" nag the A-mash keeps retriggering (every 240 frames); start the
    -- recorded route 157 frames after one, as on the original ROM. A fixed start frame broke once the English text
    -- shifted the nag's phase (the route's first steps were eaten by an open nag box).
    tutRouteT = L.frame - tutStart + 157
  end
  local eventScript = scene.kind == "event" and emu.read16(EVENT_SCRIPTS + 2 * tonumber(scene.arg), MEM) or -1
  if scene.kind == "fscript" and stage == "fwalk" and r16(ROOM) == 15 then
    -- the reception's room-load script (331, fades the room in) runs; then up to the counter and talk
    set_stage("ftalk")
    play(parse_route("90 -;60 up;6 a;60 -"))
  elseif scene.kind == "fscript" and stage == "ftalk" then
    -- arg "N[ route]": the receptionist's talk script becomes script N, then the route plays
    local want = tonumber(scene.arg:match("^%s*(%d+)"))
    local route = scene.arg:match("^%s*%d+%s+(.+)$")
    emu.setState({ ["cpu.r1"] = want })
    L.log(string.format("SCRIPT %d -> %d (hijacked in room %d) f%d", idx, want, r16(ROOM), L.frame))
    set_stage("done")
    if route then play(parse_route("1 -;" .. route)); arriveAfterRoute = true else arrive() end
    return
  end
  if (scene.kind == "menu" or scene.kind == "fscript" or scene.kind == "dmode") and stage == "title" and idx == 1 then
    tutStart = L.frame
    set_stage("tutorial")
  end
  if scene.kind == "resume" and stage == "resume" then
    set_stage("done")
    local route = scene.arg:match("|%s*(.+)$")
    if route then play(parse_route("1 -;" .. route)); arriveAfterRoute = true else arrive() end
    return
  end
  if stage ~= "done" and (scene.kind == "script" or scene.kind == "newgame" or (stage == "walk" and idx == eventScript)) then
    set_stage("done")
    if not arriveAfterRoute then arrive() end
  end
end)

-- Every string handed to the message-box text drawer (r0 = SJIS pointer), for text coverage.
L.on_exec(TEXT_DRAW, TEXT_DRAW, function()
  local p = emu.getState()["cpu.r0"]
  L.log(string.format("TEXT %08X f%d", p, L.frame))
end)

local cityFrame = nil
L.on_frame(function(n)
  if stage == "tutorial" then
    -- kind "menu": play the whole tutorial (script 1) as recorded: A every 40 frames for TUT_MASH frames, then the
    -- recorded route (Gachasute walk, Dyna names, house, sector build with an item shop), ending on the city road.
    local t = n - tutStart
    local routeT = tutRouteT or (TUT_MASH + 600)  -- fallback if no nag was seen
    if t < routeT and t > 0 and t % 40 == 0 then L.press("a", 6) end
    if t == routeT then
      local f = assert(io.open(TUT_ROUTE, "r"))
      local str = f:read("a"); f:close()
      play(parse_route(str:gsub("%s+$", "")))
    end
    if t > routeT and L.route_done() then
      if r16(ROOM) ~= 0 or r16(SCR + 0x10) ~= 0 then
        L.log(string.format("WARP tutorial route ended off the city road room=%d op=%d f%d", r16(ROOM),
          r16(SCR + 0x10), n))
      end
      if scene.kind == "fscript" then
        -- walk into the reception (room 15), whose load starts script 331 (lr 0x0805003B)
        set_stage("fwalk")
        play(parse_route("90 up;50 right;60 up;60 -"))
      elseif scene.kind == "dmode" then
        set_stage("dquit")
        play(parse_route(QUIT_ROUTE))
      else
        set_stage("done")
        play(parse_route("1 -;" .. scene.arg))
        arriveAfterRoute = true
      end
    end
  elseif stage == "dquit" then
    if L.route_done() and n - stageFrame > 900 then L.fail("dmode: the quit route set no mode") end
  elseif stage == "fwalk" or stage == "ftalk" then
    if L.route_done() and n - stageFrame > 600 then L.fail("fscript: no script started at stage " .. stage) end
  elseif stage == "boot" then
    -- logos and the date prompt: A every 60 frames until the profile form handler runs
    if n % 60 == 0 and n > 300 then L.press("a", 6) end
  elseif stage == "form" and L.route_done() then
    set_stage("title")
  elseif stage == "title" then
    if scene.kind == "boot" and scene.arg == "title" and n - stageFrame > 500 then set_stage("done"); arrive() end
    -- still on the form (the cursor missed おわる): down to the last item, then A
    if formLast >= n - 2 and L.route_done() then
      play(parse_route("6 down;30 -;6 down;30 -;6 down;30 -;6 down;30 -;6 a;60 -"))
    -- intro animation and title: Start every 120 frames until the first script starts
    elseif formLast < n - 120 and (n - stageFrame) % 120 == 0 then L.press("start", 6) end
  elseif stage == "walk" then
    -- out of the reception (room 15) by its south door into the city, where the picked event starts
    if scene.kind == "field" and r16(ROOM) == 0 and r16(SCR + 0x10) == 0 then
      if not cityFrame then cityFrame = n end
      if n - cityFrame >= 90 then
        set_stage("done")
        play(parse_route("1 -;" .. scene.arg))
        arriveAfterRoute = true
      end
    elseif scene.kind == "field" and r16(ROOM) == 0 then
      -- a script in the city (the partner Dyna greets you, script 791): click through it
      cityFrame = nil
      if L.route_done() then L.press("a", 6); L.press("-", 34) end
    else
      cityFrame = nil
      if L.route_done() and n - stageFrame > 120 then L.press("down", 20); L.press("-", 10) end
    end
  end
  if arriveAfterRoute and L.route_done() then arriveAfterRoute = false; arrive() end
  if arrived and n - arrived == hold then
    L.shot("hold.png")
    L.log(string.format("HOLD done f%d", n))
    if WARP_STATE then L.save_state(WARP_STATE, function() L.finish(0) end)
    elseif FINISH then L.finish(0) end
  end
  if arrived and n > arrived and ((MASHA or 0) > 0 or (scene.kind == "resume" and scene.arg:match("mash")))
    and (n - arrived) % 40 == 0 then L.press("a", 6) end
  if n % 30 == 0 then  -- log top-level mode changes ("MODE n")
    local m = emu.read32(MODE_VAR, MEM)
    if m ~= lastMode then L.log(string.format("MODE %d f%d", m, n)); lastMode = m end
  end
end)
