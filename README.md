# Python Socket Client and API for Bizhawk

Interact with [Bizhawk](http://tasvideos.org/Bizhawk.html) via a socket server hosted in the Lua Console.

## How to use

### Bizhawk Lua

#### Exporting

Exporting the lua hook is currently not supported as development has been moved from the .zip to its own independent repo. This feature will either be updated or removed entirely.

### Python

All Python usage is currently built around the `Memory` object for legacy reasons. This approach will most likely be changed in future updates.

You can read from and write to memory by using a `Memory` object.
```py
from bizhook import Memory

combined_wram = Memory('Combined WRAM')
```

To see the available methods, do `help(Memory)`.

#### Memory domain
You can use the default memory domain by providing an empty string. However, I would advice against it and that you always do specify with which domain you want to interact. It may be that it works for you solely because, per chance, the default one happens to be the correct one.

## Credits

This project is based on code written by Maximillian Strand. It should be noted that despite having the same name, these projects are not compatible or interchangeable as the API has been changed completely. 
