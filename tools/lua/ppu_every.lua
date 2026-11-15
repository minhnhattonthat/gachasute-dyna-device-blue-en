-- Dump video memory every 30 frames (ppu_<frame>.*) beside a regen.py run: the last dump shows the scene's hold.
--   python -X utf8 tools/debug/regen.py SCENE --out work/qa/menu_dump --probe tools/lua/ppu_every.lua
L.on_frame(function(f)
  if f % 30 == 0 then L.dump_ppu(string.format("ppu_%06d", f)) end
end)
