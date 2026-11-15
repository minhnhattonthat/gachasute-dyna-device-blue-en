-- Screenshots (shotwhen_NN.png) from the first frame whose OAM shows a sprite with OBJ tile SW_TILE (default 397: the
-- title's blinking PRESS START), for blinking or timed sprites. Run beside warp.lua:
--   regen.py mode_title --rom build/dynadevice_blue_en.gba --probe tools/lua/shotwhen.lua
local WANT, done, at = tonumber(SW_TILE) or 397, false, nil
L.on_frame(function()
  -- 2 frames on: the picture lags the OAM; then every 10 frames (SW_SHOTS shots): a blink may hide it by blending
  if at and L.frame >= at and (L.frame - at) % 10 == 0 and (L.frame - at) // 10 < (tonumber(SW_SHOTS) or 30) then
    L.shot(string.format("shotwhen_%02d.png", (L.frame - at) // 10))
  end
  if done or L.frame < (tonumber(SW_FROM) or 640) then return end
  for i = 0, 127 do
    local a0 = emu.read(8 * i + 1, emu.memType.gbaSpriteRam)
    local t = emu.read(8 * i + 4, emu.memType.gbaSpriteRam) + 256 * (emu.read(8 * i + 5, emu.memType.gbaSpriteRam) & 3)
    if (a0 & 3) ~= 2 and t == WANT then
      done, at = true, L.frame + 2
      local function h(k) return emu.read(8 * i + k, emu.memType.gbaSpriteRam) + 256 * emu.read(8 * i + k + 1, emu.memType.gbaSpriteRam) end
      L.log(string.format("SHOTWHEN tile %d f%d oam %d: %04X %04X %04X BLDCNT %04X", WANT, L.frame, i, h(0), h(2), h(4),
        emu.read(0x04000050, emu.memType.gbaMemory) + 256 * emu.read(0x04000051, emu.memType.gbaMemory)))
      return
    end
  end
end)
