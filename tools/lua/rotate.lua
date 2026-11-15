-- Text coverage by sibling rotation (tools/debug/rotate.py writes the groups). Run beside warp.lua and
-- textcover.lua: when the text renderer 0x080049AC draws an entry of a pointer table that still has unshown
-- strings, the text object is pointed at the next unshown sibling, so the game reads and draws it in the same window.
--   --var "ROT_EVERY=1"   substitute on every Nth matching render call (default 1)
--   --var "ROT_HOLD=3"    rewind mode: snapshot the machine at the first substitution, and every ROT_HOLD frames load
--                         it back and substitute the next unshown sibling, until the group is used up (0 = off: one
--                         substitution per draw, so a static screen covers one sibling per entry it draws)
-- Not run directly: tools/debug/rotate.py writes work/qa/rotate_probe.lua = ROT_GROUPS + this file (Mesen's working
-- directory isn't the repo, so the groups can't be loaded by path).
local G = ROT_GROUPS
local every = ROT_EVERY or 1
local hold = ROT_HOLD or 3
local of = {}      -- address -> group
for _, g in ipairs(G) do
  g.next = 1
  for _, a in ipairs(g.all) do of[a] = g end
end
local calls = 0
local snap = nil  -- {state, group, apply(n), frame}: rewind point while a group still has siblings left
local lastSet = nil
local function r32(a) return emu.read32(a, emu.memType.gbaMemory, false) end
local function take(g)
  if g.next > #g.un then return nil end
  local n = g.un[g.next]
  g.next = g.next + 1
  lastSet = n
  return n
end
local function pick(p, apply)
  if p == lastSet then return end  -- the hook refiring on an instruction we already redirected (after a load)
  if ROT_WAIT and not (WARP_DONE or WARP_ARRIVED) then return end  -- rotate.py --any: keep the warp's own draws
  local g = of[p]
  if not g or g.next > #g.un then return end
  calls = calls + 1
  if calls % every ~= 0 then return end
  if hold > 0 and not snap and g.next < #g.un and (WARP_DONE or WARP_ARRIVED) then
    snap = { state = emu.createSavestate(), group = g, apply = apply, frame = L.frame, born = L.frame,
             touched = {}, done = -1 }
  end
  if snap then snap.touched[g] = true end
  local n = take(g)
  L.log(string.format("ROT f%d %08X -> %08X", L.frame, p, n))
  apply(n)
end
-- Renderer: text objects pointing straight at ROM (most UI text is copied to a stack buffer first, see below).
L.on_exec(0x080049AC, 0x080049AC, function()
  local o = emu.getState()["cpu.r0"]
  pick(r32(o), function(n) emu.write32(o, n, emu.memType.gbaMemory) end)
end)
-- Expander 0x0801328C (r0 = dst buffer, r1 = source string): the usual path of menu and help text.
L.on_exec(0x0801328C, 0x0801328C, function()
  pick(emu.getState()["cpu.r1"], function(n) emu.setState({["cpu.r1"] = n}) end)
end)
-- Text slot setter 0x08013D18 (r0 = slot, r1 = mode, r2 = string): description boxes (item, shop, sell, DB help)
-- take their lines from the flat pointer table 0x0BDAE8 through it, and never pass the two hooks above.
L.on_exec(0x08013D18, 0x08013D18, function()
  pick(emu.getState()["cpu.r2"], function(n) emu.setState({["cpu.r2"] = n}) end)
end)
-- Rewind: savestates load only inside an exec callback, so arm a one-shot hook on any instruction.
-- Every group drawn after the snapshot is redrawn by the replay, so keep rewinding while any of them has siblings
-- left and the last rewind used some up (a replay that draws none of them would otherwise loop for ever).
local loading = false
local function progress(s)
  local left, used = false, 0
  for g in pairs(s.touched) do
    used = used + g.next
    if g.next <= #g.un then left = true end
  end
  return left, used
end
local loadingSince = 0
L.on_frame(function()
  -- Watchdog: a sibling drawn in the wrong kind of slot can crash the game; give up on a chain that stalls, so the
  -- warp still takes its hold shot (ROT_BUSY) and the run ends.
  if snap and (L.frame - snap.born > 6000 or (loading and L.frame - loadingSince > 60)) then
    L.log(string.format("ROT f%d gave up a rewind chain", L.frame))
    snap, loading = nil, false
    return
  end
  -- Rewinds start once the route is done, so they never eat its presses. A replay then lacks any press made after
  -- the snapshot, which is harmless here: the redirected draw happens at the snapshot itself (rotation runs are
  -- coverage only; their hold shots are not visual QA).
  if not snap or loading or not L.route_done() or L.frame - snap.frame < hold then return end
  -- Snapshots are taken only once the warp's RAM writes (mode jumps) are over (WARP_DONE), since a rewind past them
  -- stalls the warp; rewinds wait for arrival, so the replays can't hide the scene from the warp's arrival check.
  if not WARP_ARRIVED then return end
  local s = snap
  local left, used = progress(s)
  if not left or used == s.done then snap = nil; return end
  s.done = used
  loading, loadingSince = true, L.frame
  local id
  id = L.on_exec(0x00000000, 0x0FFFFFFF, function()
    if not loading or snap ~= s then return end
    loading = false
    emu.removeMemoryCallback(id, emu.callbackType.exec, 0x00000000, 0x0FFFFFFF, emu.cpuType.gba,
      emu.memType.gbaMemory)
    emu.loadSavestate(s.state)
    lastSet = nil
    local n = take(s.group)
    if n then
      L.log(string.format("ROT f%d rewind -> %08X", L.frame, n))
      s.apply(n)
    else
      L.log(string.format("ROT f%d rewind", L.frame))
    end
    s.frame = L.frame
  end)
end)
-- warp.lua waits for this before its hold shot, so a rewind chain started late in the hold isn't cut short.
function ROT_BUSY() return snap ~= nil end
