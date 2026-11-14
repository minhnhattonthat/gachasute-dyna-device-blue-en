-- Marker-build probe (phase 5 width gate): on every call of the text renderer 0x080049AC whose string starts with
-- a marker id (5 hex digits = string offset, or sSSS.KK: = message), log once per (id, place):
--   MARK id size=S col=C row=R units=N
-- col/row: the text's map cell (from the map VRAM address +0x14, 32 cells per row). Run beside warp.lua on a
-- build.py --marker ROM; tools/debug/regen.py --probe tools/lua/markerlog.lua.
local seen = {}
local function r8(a) return emu.read(a, emu.memType.gbaMemory, false) end
local function r32(a) return emu.read32(a, emu.memType.gbaMemory, false) end
local function hex(c) return (c >= 48 and c <= 57) or (c >= 65 and c <= 70) end
L.on_exec(0x080049AC, 0x080049AC, function()
  local o = emu.getState()["cpu.r0"]
  local p = r32(o)
  if p < 0x02000000 or p >= 0x0A000000 then return end
  local b = {}
  for i = 0, 8 do b[i] = r8(p + i) end
  local id
  if b[0] == 115 and b[4] == 46 and b[7] == 58 then          -- sSSS.KK:
    id = string.char(b[0], b[1], b[2], b[3], b[4], b[5], b[6])
  elseif hex(b[0]) and hex(b[1]) and hex(b[2]) and hex(b[3]) and hex(b[4]) and not hex(b[5]) then
    id = "t0" .. string.char(b[0], b[1], b[2], b[3], b[4])
  end
  if not id then return end
  local map = r32(o + 0x14)
  local cell = ((map & 0x7FF) // 2)
  local key = string.format("%s %d %d", id, cell, r8(o + 5))
  if seen[key] then return end
  seen[key] = true
  local n = r8(o + 4)
  if n == 0 then
    while emu.read16(p + 2 * n, emu.memType.gbaMemory, false) ~= 0 and n < 255 do n = n + 1 end
  end
  L.log(string.format("MARK %s size=%d col=%d row=%d units=%d map=%08X f%d", id, r8(o + 5), cell % 32,
    cell // 32, n, map, L.frame))
end)
