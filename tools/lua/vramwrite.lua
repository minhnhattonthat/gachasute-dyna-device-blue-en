-- Log the first writes into an OBJ VRAM range (default: the PDA home label アドレス, OBJ tiles 172-175):
-- frame, address, value, pc, lr, r0-r3. Run beside warp.lua: regen.py SCENE --probe tools/lua/vramwrite.lua
local LO, HI, n = 0x06011580, 0x060115FF, 0
L.on_write(LO, HI, function(addr, value)
  if not value or value == 0 or L.frame < (tonumber(VW_FROM) or 600) then return end   -- skip clears / boot screens
  n = n + 1
  if n > 40 then return end
  local st = emu.getState()
  local function r(i) return st["cpu.r" .. i] or st["cpu.r[" .. i .. "]"] or 0 end
  L.log(string.format("VW f%d %08X=%X pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X", L.frame, addr, value or 0,
    r(15), r(14), r(0), r(1), r(2), r(3)))
end)
