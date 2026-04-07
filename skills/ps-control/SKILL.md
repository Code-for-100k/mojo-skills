---
name: ps-control
description: Configure PS5 DualSense controller button mappings, joystick sensitivity, and chords for the ControllerKeys macOS app. Use this skill whenever the user wants to remap controller buttons, adjust mouse/scroll sensitivity, add button combos, view current mappings, or troubleshoot controller input. Trigger on any mention of PS5 controller, DualSense, ControllerKeys, button mapping, controller sensitivity, joystick settings, remap buttons, or controller configuration. Also trigger when user says things like "make L1 do X", "what does Triangle do", "mouse is too slow/fast", or "add a shortcut to my controller".
---

# PS Control — ControllerKeys Configuration Skill

You configure the user's PS5 DualSense controller mappings by editing `~/.controllerkeys/config.json` directly. The user describes what they want in plain language and you translate it to config changes.

## How It Works

1. Read `~/.controllerkeys/config.json`
2. Find the active profile (match `activeProfileId` to a profile's `id`)
3. Make the requested change to that profile's `buttonMappings`, `chordMappings`, or `joystickSettings`
4. Back up the current config: `cp ~/.controllerkeys/config.json ~/.controllerkeys/backups/config_$(date +%Y-%m-%d_%H-%M-%S).json`
5. Write the modified config
6. Tell the user to restart ControllerKeys (Cmd+Q then reopen) for changes to take effect

## PS5 Button → Config Key Mapping

| PS5 Button | Config Key | Notes |
|------------|-----------|-------|
| X (Cross) | `a` | Bottom face button |
| Circle | `b` | Right face button |
| Square | `x` | Left face button |
| Triangle | `y` | Top face button |
| L1 | `leftBumper` | Left shoulder |
| R1 | `rightBumper` | Right shoulder |
| L2 | `leftTrigger` | Left trigger |
| R2 | `rightTrigger` | Right trigger |
| L3 | `leftThumbstick` | Left stick click |
| R3 | `rightThumbstick` | Right stick click |
| D-Pad Up | `dpadUp` | |
| D-Pad Down | `dpadDown` | |
| D-Pad Left | `dpadLeft` | |
| D-Pad Right | `dpadRight` | |
| Options | `menu` | Right small button |
| Share/Create | `view` | Left small button |
| PS Button | `xbox` | Center button |
| Mic Button | `micMute` | Below touchpad |
| Touchpad Click | `touchpadButton` | Press touchpad |
| Touchpad Tap | `touchpadTap` | Tap touchpad |
| Touchpad 2-Finger Click | `touchpadTwoFingerButton` | |
| Touchpad 2-Finger Tap | `touchpadTwoFingerTap` | |

## macOS Key Codes

Use these numeric codes in the `keyCode` field:

**Letters:**
A=0, S=1, D=2, F=3, H=4, G=5, Z=6, X=7, C=8, V=9, B=11, Q=12, W=13, E=14, R=15, Y=16, T=17, O=31, U=32, I=34, P=35, L=37, J=38, K=40, N=45, M=46

**Numbers:**
1=18, 2=19, 3=20, 4=21, 5=23, 6=22, 7=26, 8=28, 9=25, 0=29

**Symbols:**
-=27, +=24, [=33, ]=30, ;=41, '=39, \=42, ,=43, .=47, /=44, `=50

**Special Keys:**
Return/Enter=36, Tab=48, Space=49, Delete/Backspace=51, Escape=53, Forward Delete=117

**Arrows:**
Left=123, Right=124, Down=125, Up=126

**Function Keys:**
F1=122, F2=120, F3=99, F4=118, F5=96, F6=97, F7=98, F8=100, F9=101, F10=109, F11=103, F12=111, F13=105, F19=80

**Mouse Buttons:**
Left Click=61440, Right Click=61441, Middle Click=61442

## Config Structures

### Button Mapping

```json
{
  "isHoldModifier": false,
  "keyCode": 36,
  "modifiers": {
    "command": false,
    "control": false,
    "option": false,
    "shift": false
  }
}
```

Optional additions to a button mapping:

**Long hold** (fires different action when held):
```json
"longHoldMapping": {
  "keyCode": 36,
  "modifiers": {"command": true, "control": false, "option": false, "shift": false},
  "threshold": 0.5
}
```

**Double tap:**
```json
"doubleTapMapping": {
  "keyCode": 0,
  "modifiers": {"command": true, "control": false, "option": false, "shift": false}
}
```

**Key repeat** (for arrow keys, scrolling):
```json
"repeatMapping": {"enabled": true, "interval": 0.05}
```

**Hold modifier** (button acts like Cmd/Ctrl/etc while held):
Set `"isHoldModifier": true` and put the modifier in `modifiers`. The `keyCode` can be `null` or a special value like 61440.

### Chord Mapping (two buttons pressed together)

```json
{
  "buttons": ["rightBumper", "x"],
  "id": "GENERATE-A-UUID",
  "keyCode": 51,
  "modifiers": {"command": true, "control": false, "option": false, "shift": false}
}
```

Generate a new UUID for each chord using Python: `str(uuid.uuid4()).upper()`

Chords can also have a `"hint"` field for display and a `"systemCommand"` field for shell commands.

### Joystick Settings

All values are 0.0 to 1.0 unless noted:

| Setting | What It Controls | User-Friendly Name |
|---------|-----------------|-------------------|
| `mouseSensitivity` | Base cursor speed | "mouse speed" |
| `mouseAcceleration` | How much speed increases with stick deflection | "mouse acceleration" |
| `mouseDeadzone` | Minimum stick movement before cursor moves (prevents drift) | "mouse deadzone" |
| `scrollSensitivity` | Base scroll speed | "scroll speed" |
| `scrollAcceleration` | Scroll speed increase with stick deflection | "scroll acceleration" |
| `scrollDeadzone` | Minimum stick movement for scrolling | "scroll deadzone" |
| `scrollBoostMultiplier` | Multiplier when stick is fully deflected (1-10) | "scroll boost" |
| `invertMouseY` | Invert vertical mouse movement (boolean) | "invert mouse" |
| `invertScrollY` | Invert scroll direction (boolean) | "invert scroll" |
| `leftStickMode` | What left stick does: "mouse", "scroll", "dpad" | "left stick mode" |
| `rightStickMode` | What right stick does: "mouse", "scroll", "dpad" | "right stick mode" |
| `gyroAimingEnabled` | Enable motion-controlled cursor (boolean) | "gyro aiming" |
| `gyroAimingSensitivity` | Motion control sensitivity | "gyro sensitivity" |
| `gyroAimingDeadzone` | Motion control deadzone | "gyro deadzone" |
| `touchpadSensitivity` | Touchpad cursor speed | "touchpad speed" |
| `touchpadAcceleration` | Touchpad acceleration curve | "touchpad acceleration" |
| `touchpadSmoothing` | Touchpad movement smoothing (higher = smoother but laggier) | "touchpad smoothing" |
| `focusModeSensitivity` | Reduced sensitivity when focus modifier is held | "precision mode speed" |

## Translating User Requests

When the user says "make [button] do [action]", translate it like this:

1. Map the PS5 button name to the config key (see table above)
2. Figure out the keyCode and modifiers for the desired action:
   - "browser back" = keyCode 33 ([), modifiers command=true (Cmd+[)
   - "browser forward" = keyCode 30 (]), modifiers command=true (Cmd+])
   - "copy" = keyCode 8 (C), modifiers command=true
   - "paste" = keyCode 9 (V), modifiers command=true
   - "undo" = keyCode 6 (Z), modifiers command=true
   - "redo" = keyCode 6 (Z), modifiers command=true, shift=true
   - "app switcher" / "Cmd+Tab" = keyCode 48 (Tab), modifiers command=true
   - "Mission Control" = keyCode 99 (F3)
   - "Spotlight" / "Cmd+Space" = keyCode 49 (Space), modifiers command=true
   - "close tab" = keyCode 13 (W), modifiers command=true
   - "new tab" = keyCode 17 (T), modifiers command=true
   - "screenshot" = keyCode 20 (4), modifiers command=true, shift=true
3. Read the current config, modify the button, write it back

## Showing Current Mappings

When the user asks "what's mapped to X" or "show all mappings", read the config and present a human-readable table. Translate config keys back to PS5 button names, keyCodes back to key names, and show modifiers as "Cmd+", "Ctrl+", etc.

## Important Notes

- Always back up before writing changes
- Always work with the active profile only (match `activeProfileId`)
- Use `python3` for JSON manipulation (it's available on the user's Mac)
- After changes, remind the user to restart ControllerKeys
- If the user asks to "show" or "list" mappings, just read and display — don't modify anything
- Be conversational — confirm what you're about to change before doing it
