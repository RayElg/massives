# massives
N-Body simulation written with Rust and Python.

![Simulation portraying 3-body system](https://raynorelgie.com/showcase.gif)

Simulates gravitational effects on velocity as well as basic collision of bodies.  
Two colliding bodies become one body with a larger mass, radius, and new velocity.  
  
Exposes Rust structs and a function to Python using Python ctypes library and Rust extern.  
Reads in bodies to simulate from ``massives.json``  

### Running

#### Windows users:
If your architecture is compatible with mine, you can run simply ``run.py`` with python3. This will load the precompiled .dll and begin simulating the system read from ``massives.json``.

### MacOS/Linux:
Run ``cargo build --release`` from ``./massives``. This will compile the library to ./massives/target/release.  
Then, configure the ``lib = ctypes.cdll.LoadLibrary("./target/release/massives.dll")`` statement in run.py to match with your operating system's file extension. (.so, .dylib, etc.)

### Controls
* W, S for zoom
* A, D for tick speed
* Arrow keys to pan

### Simulating other systems

Add, modify, or replace entries in the "massives" list in the massives.json file. In theory, you could simulate as many bodies as you have memory for.

For example, you could add
```json
,{
            "mass": 6000.0,
            "vel_x": -2,
            "vel_y": -1,
            "pos_x": -4900.0,
            "pos_y": 9000.0,
            "radius": 3000
}
```
between lines 26 and 27 of ``massives.json`` to simulate a massive object passing by the existing system.

You can simulate binary star systems, planets with dozens of tightly packed moons, or a system like our own solar system.

### TODO:
* More error handling (unsafe rust code)
* More controls
* Save/load systems during execution
