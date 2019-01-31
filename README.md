Some scripts for testing with the Looking Glass 3D display.

Concepts:

- "quilt image": NxM views collected in a single image, usually 
  2048x2048 or 4096x4096. This is the standard method used by the 
  Looking Glass tooling to store multi-view content. To display a 
  quilt image on a Looking Glass the per-device calibration values 
  are used to generate a native image on the fly, usually in done a fragment shader.
- "native image": An image in the native resolution of a Looking Glass 
  display, 2560x1600 for a small LG model, which can be directly 
  displayed on the device. This image is only viewable correctly on 
  the specific device being targeted, as it uses the per-device calibration values.

Scripts:

- `get_calibration_from_eeprom.py`: Get the display calibration values
  (in the form of a JSON string) from a Looking Glass. Save this to
  a .json file, as some of the other scripts need these values.
- `make_quilt.py`: Generate a standard quilt from a set of view images
- `gen_numbers_quilt.py`: Generates a quilt where each tile shows the 
  view number. This can be used to (try to) understand how the 
  individual views (and their pixels) are shown on the Looking Glass
- `quilt2native.py`: Takes a standard quilt and outputs a native image, 
  based on a device's calibration values. This should match what the 
  official LG tools do.
- `linquilt2native.py`: Takes a linear quilt (all tile images 
  side-by-side, i.e. num vertical tiles = 1) and outputs a native image.
- `frames2native.py`: Reads a set of separate tile images and output 
  a native image. 
