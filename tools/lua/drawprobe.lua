-- Text-render probe (phase 5): logs each call of the text-object renderer 0x080049AC (first N calls after
-- frame F): obj fields and the message drawer state 0x02001AC0. Run beside warp.lua.
--   --var "F=0" --var "N=200"
local from = F or 0
local left = N or 200
local function r8(a) return emu.read(a, emu.memType.gbaMemory, false) end
local function r16(a) return emu.read16(a, emu.memType.gbaMemory, false) end
local function r32(a) return emu.read32(a, emu.memType.gbaMemory, false) end
L.on_exec(0x080049AC, 0x080049AC, function()
  if L.frame < from or left <= 0 then return end
  left = left - 1
  local s = emu.getState()
  local o = s["cpu.r0"]
  local p = r32(o)
  local units = {}
  for i = 0, 5 do units[#units + 1] = string.format("%04X", r16(p + 2 * i)) end
  local st = {}
  for i = 0, 0x17 do st[#st + 1] = string.format("%02X", r8(0x02001AC0 + i)) end
  L.log(string.format("f%d lr=%08X obj=%08X str=%08X len=%d size=%d pal=%d fg=%d bg=%d tile=%X vram=%08X map=%08X | %s | S %s",
    L.frame, s["cpu.r14"] or 0, o, p, r8(o + 4), r8(o + 5), r8(o + 6), r8(o + 7), r8(o + 8), r32(o + 0xc),
    r32(o + 0x10), r32(o + 0x14), table.concat(units, " "), table.concat(st, " ")))
end)
