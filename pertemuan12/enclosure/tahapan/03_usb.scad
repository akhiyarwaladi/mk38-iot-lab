L = 110;
W = 80;
H = 35;
wall = 2;
floor_t = 2;
difference() {
  cube([L,W,H]);
  translate([wall,wall,floor_t]) cube([L-2*wall,W-2*wall,H]);
  // Pemotong melampaui kedua permukaan wall agar bukaan tembus.
  translate([-0.1,W/2-7,8]) cube([wall+0.2,14,10]);
}
