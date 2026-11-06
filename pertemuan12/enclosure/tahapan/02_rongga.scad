L = 110;
W = 80;
H = 35;
wall = 2;
floor_t = 2;
difference() {
  cube([L,W,H]);
  translate([wall,wall,floor_t]) cube([L-2*wall,W-2*wall,H]);
}
