-- Fake device-development projects for the dev status screen (mode 21, scenes d_dev_proj*): the tutorial save has
-- none, so the status words / info panel (block 01EE624, PAT 01EF514 frames 17-21) never show. Line L (Project A-D)
-- is 0x64 bytes at 0x02008960 + 0x64 * L, +0 = in use (read by 0x08059BCA / 0x08011B10); its slot s is 24 bytes at
-- +4 + 24 * s (readers 0x0801185C.. 0x080119E4, args line = s8 0x02011894, slot = s8 0x020118E0): +1 s8 kind,
-- +3 s8 status (frame 17 + status: 0 no problem, 1 no funds, 2 no parts, 3 done), +6 / +8 s16.
-- Line L / slot s gets status (L + s) % 4; the list shows A..D = No Issues / Low Funds / Low Parts / Complete. The
-- key +1/+2 = 0x0E/0x10 is what 0x08011AFC (find line) asks for on the tutorial save. Run beside warp.lua; DP_FROM (frame, default 600) delays the writes until the save is loaded.
local MEM = emu.memType.gbaMemory
local FROM = tonumber(DP_FROM) or 600
-- slot +1: KIND 3 gives the detail page with the frame 21 info panel (0x08068EFA: KIND / 3 <= 4); 15+ garbles it
local KIND = tonumber(DP_KIND) or 3
L.on_exec(0x08011AFC, 0x08011AFC, function()
  local st = emu.getState()
  L.log(string.format("devproj: find line r0=%X r1=%X lr=%08X", st["cpu.r0"] or 0, st["cpu.r1"] or 0, st["cpu.r14"] or 0))
end)
L.on_frame(function()
  if L.frame < FROM then return end
  for line = 0, 3 do
    local b = 0x02008960 + 0x64 * line
    emu.write(b, 1, MEM)
    emu.write(b + 1, 0x0E, MEM)   -- the key 0x08011AFC looks for on the tutorial save (factory location?)
    emu.write(b + 2, 0x10, MEM)
    emu.write(b + 3, line, MEM)
    for s = 0, 3 do
      local a = b + 4 + 24 * s
      emu.write(a, 1, MEM)
      emu.write(a + 1, KIND, MEM)
      emu.write(a + 2, 1, MEM)
      emu.write(a + 3, (line + s) % 4, MEM)
      emu.write(a + 6, 50, MEM); emu.write(a + 7, 0, MEM)
      emu.write(a + 8, 20 + 10 * s, MEM); emu.write(a + 9, 0, MEM)
    end
  end
end)
