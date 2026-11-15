-- Log each sprite object's animation frame as the sprite drawer (0x0800169C) reads it, once per distinct frame data
-- pointer: object, anim base [obj+0x18], frame index [obj+0x24], frame data address, OBJ tile base [obj+0x38].
-- Run beside warp.lua: regen.py SCENE --probe tools/lua/animframe.lua   (AF_FROM: first frame to log, default 600)
local seen, n = {}, 0
L.on_exec(0x080016C2, 0x080016C2, function()
  if L.frame < (tonumber(AF_FROM) or 600) then return end
  local st = emu.getState()
  local function r(i) return st["cpu.r" .. i] or st["cpu.r[" .. i .. "]"] or 0 end
  local fd, obj = r(0), r(1)
  if seen[fd] or n > 80 then return end
  seen[fd] = true
  n = n + 1
  local m = emu.memType.gbaMemory or emu.memType.cpuMemory
  local sl = st["cpu.r10"] or 0
  L.log(string.format("AF f%d sl=%08X base=%08X frame=%d fd=%08X tilebase=%d", L.frame, sl,
    emu.read32(sl, m, false), emu.read16(sl + 0xC, m, true), fd, emu.read16(sl + 0x20, m, false)))
end)
