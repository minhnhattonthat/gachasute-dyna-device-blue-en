-- Text coverage by sibling rotation (tools/debug/rotate.py writes the groups). Run beside warp.lua and
-- textcover.lua: when the text renderer 0x080049AC draws an entry of a pointer table that still has unshown
-- strings, the text object is pointed at the next unshown sibling, so the game reads and draws it in the same window.
--   --var "ROT_EVERY=1"   substitute on every Nth matching render call (default 1)
-- Not run directly: tools/debug/rotate.py writes work/qa/rotate_probe.lua = ROT_GROUPS + this file (Mesen's working
-- directory isn't the repo, so the groups can't be loaded by path).
local G = ROT_GROUPS
local every = ROT_EVERY or 1
local of = {}      -- address -> group
for _, g in ipairs(G) do
  g.next = 1
  for _, a in ipairs(g.all) do of[a] = g end
end
local calls = 0
local function r32(a) return emu.read32(a, emu.memType.gbaMemory, false) end
local function pick(p)
  local g = of[p]
  if not g or g.next > #g.un then return nil end
  calls = calls + 1
  if calls % every ~= 0 then return nil end
  local n = g.un[g.next]
  g.next = g.next + 1
  L.log(string.format("ROT f%d %08X -> %08X", L.frame, p, n))
  return n
end
-- Renderer: text objects pointing straight at ROM (most UI text is copied to a stack buffer first, see below).
L.on_exec(0x080049AC, 0x080049AC, function()
  local o = emu.getState()["cpu.r0"]
  local n = pick(r32(o))
  if n then emu.write32(o, n, emu.memType.gbaMemory) end
end)
-- Expander 0x0801328C (r0 = dst buffer, r1 = source string): the usual path of menu and help text.
L.on_exec(0x0801328C, 0x0801328C, function()
  local n = pick(emu.getState()["cpu.r1"])
  if n then emu.setState({["cpu.r1"] = n}) end
end)
