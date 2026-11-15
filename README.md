# Gachasute! Dyna Device Blue English translation

Unofficial English fan translation of **Gachasute! Dyna Device Blue** (Game Boy Advance, Smilesoft, 2002): the source
text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Base ROM

| | Blue | Red |
|---|---|---|
| No-Intro name | Gachasute! Dyna Device Blue (Japan) | Gachasute! Dino Device Red (Japan) |
| Size | 8388608 bytes | 8388608 bytes |
| CRC32 | EB9F6F11 | DDA5EC5E |
| MD5 | 5cc9b8d313d1ee5ea7c994dc18f85b95 | 23a1a8685d67405271f297f5a042fa23 |
| SHA-1 | eac296b55bea162df72e417a501be70060bd1337 | 9086aa71d23a753cf0e307a37d56c61c3805adb6 |

Each version has its own patch (a Blue patch refuses a Red dump). The two ROMs differ only in their header and a
version flag, so both get the same translation. The patched ROM's CRC32 and SHA-1 are in the release zip's README. Start from a cold boot (no savestates from the
Japanese version). Tested in Mesen 2.2.1 (GBA core) with the official BIOS.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story (all event scripts) | Translated |
| Menus, items, Dyna, Devices, PDA apps, help pages, system messages | Translated |
| Title screen and graphics with text | Redrawn in English |
| Name entry | English labels; the kana pages stay, names can be typed in kana or Latin letters |
| Staff roll | Redrawn in English |
| Addresses looked up from a postal code (profile, address book) | Romanized (v1.1): ~120,000 real place names in Hepburn, from Japan Post's kana readings (decision D21) |

Known issues: some names are cut to fit 64-pixel slots (e.g. "Flare Ruby"); PDA timetable subjects are 3-letter
abbreviations; link-cable trading and battles were not tested (one emulator). Postal-code addresses: about 4% of
the 2002 town names have no published reading and were read by a dictionary, so a few may be misread; very long
names are split into words or shortened (the prefecture is left out when the field is too narrow). See
[Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/gachasute-dyna-device-blue-en
cd gachasute-dyna-device-blue-en
# copy your dump to: rom/Gachasute! Dyna Device Blue (Japan).gba
#   (8388608 bytes, SHA-1 eac296b55bea162df72e417a501be70060bd1337; the build refuses any other dump, see rom.sha1)
# optional: rom/Gachasute! Dino Device Red (Japan).gba (SHA-1 9086aa71d23a753cf0e307a37d56c61c3805adb6)
python -X utf8 tools/build.py                          # -> build/dynadevice_blue_en.gba (+ dinodevice_red_en.gba)
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Smilesoft's and is included only so
the translation can be checked against it. Gachasute! Dyna Device Blue is (c) 2002 Smilesoft; this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic; review passes by OpenAI Codex).
Corrections are very welcome.
