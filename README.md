# Bizhawk Hook

Interact with [Bizhawk](http://tasvideos.org/Bizhawk.html) via a socket server hosted in the Lua Console.

## How to use

### Bizhawk Lua

#### Exporting

Export all the necessary Lua components using the provided function.
```py
from bizhook import export_lua_components

export_lua_components('/home/williamson/.bizhook')
```
You can either provide a path or leave it empty to have it open up a file dialogue asking for directory.

#### Opening socket

In Bizhawk, go to `Tools` > `Lua Console`. Select `Open script` and open `hook.lua` from the exported components.

##### Is it working?

If it starts successfully, you should see a text in the top-left of the emulator saying the socket is being opened. Should that not appear, try restarting the emulator until it does. This seems to be an issue with Bizhawk.

**Note**: Do not try to communicate with the socket *before* the text has disappeared, as it isn't actually opened yet. The message is there to make it clear that the script is running successfully.

### Python

You can read from and write to memory by using a `Memory` object.
```py
from bizhook import Memory

combined_wram = Memory('Combined WRAM')
```

To see the available methods, do `help(Memory)`.

#### Memory domain
You can use the default memory domain by providing an empty string. However, I would advice against it and that you always do specify with which domain you want to interact. It may be that it works for you solely because, per chance, the default one happens to be the correct one.