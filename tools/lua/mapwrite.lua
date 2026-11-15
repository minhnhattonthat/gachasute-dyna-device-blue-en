-- Log the CPU writes of one tile number into a VRAM / WRAM range (who builds a BG map word): frame, address,
-- value, pc, lr, r0-r3. Run beside warp.lua: regen.py SCENE --probe tools/lua/mapwrite.lua
-- Defaults: BG screen VRAM 0x06000000-0x06003FFF, tile 0x74 (any palette / flip bits), from frame 300.
-- Override by editing MW_* below or with emu.py --var MW_LO=0x.. MW_HI=0x.. MW_TILE=0x.. MW_FROM=N.
local LO = tonumber(MW_LO) or 0x06000000
local HI = tonumber(MW_HI) or 0x06003FFF
local TILE = tonumber(MW_TILE) or 0x74
local FROM = tonumber(MW_FROM) or 300
local n = 0
L.on_write(LO, HI, function(addr, value)
  if not value or L.frame < FROM or (value & 0x3FF) ~= TILE then return end
  n = n + 1
  if n > 40 then return end
  local st = emu.getState()
  local function r(i) return st["cpu.r" .. i] or st["cpu.r[" .. i .. "]"] or 0 end
  L.log(string.format("MW f%d %08X=%X pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X", L.frame, addr, value,
    r(15), r(14), r(0), r(1), r(2), r(3)))
  -- likely return addresses on the stack (odd ROM words): the callers above lr
  local sp, rets = r(13), {}
  for i = 0, 63 do
    local w = emu.read32(sp + 4 * i, emu.memType.gbaMemory, false)
    if w >= 0x08000000 and w < 0x08400000 and w % 2 == 1 then rets[#rets + 1] = string.format("%08X", w) end
  end
  L.log("MW   stack " .. table.concat(rets, " "))
end)
