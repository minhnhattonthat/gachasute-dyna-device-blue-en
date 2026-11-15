-- Log CPU writes of one OAM attribute value into work RAM (the game's OAM shadow): frame, address, value, pc, lr,
-- r0-r3. Default: attr2 0x6140 (title screen planet name, OBJ tile 320 pal 6). Run beside warp.lua:
--   regen.py mode_title --probe tools/lua/oamword.lua      (OW_VALUE / OW_FROM override as globals)
local WANT, n = tonumber(OW_VALUE) or 0x6140, 0
local function hook(addr, value)
  if not value or ((value & 0xFFFF) ~= WANT and ((value >> 16) & 0xFFFF) ~= WANT) or L.frame < (tonumber(OW_FROM) or 600) then return end
  n = n + 1
  if n > 20 then return end
  local st = emu.getState()
  local function r(i) return st["cpu.r" .. i] or st["cpu.r[" .. i .. "]"] or 0 end
  L.log(string.format("OW f%d %08X=%X pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X", L.frame, addr, value,
    r(15), r(14), r(0), r(1), r(2), r(3)))
end
L.on_write(0x03000000, 0x03007FFF, hook)
L.on_write(0x02000000, 0x0203FFFF, hook)
