// Dimensi latihan dalam mm; ukur komponen sebelum membuat enclosure akhir.
part = "base"; // "base", "lid", atau "assembly"
L = 110;
W = 80;
H = 35;
wall = 2;
floor_t = 2;
lid_t = 2;
gap = 0.4; // clearance per sisi
lip_t = 1.6;
lip_h = 3;
screw_d = 3.4;
boss_d = 7;
boss_h = 8;
inset = 8;
$fn = 48;

assert(L > 2*wall+2*gap+2*lip_t && W > 2*wall+2*gap+2*lip_t);
assert(H > floor_t+boss_h+lip_h && gap > 0 && wall > 0);
assert(screw_d < boss_d && inset > wall+gap+lip_t+boss_d/2);
assert(part == "base" || part == "lid" || part == "assembly", "part tidak dikenal");

module screw_positions() {
  for (x = [inset, L-inset], y = [inset, W-inset])
    translate([x,y,0]) children();
}

module base() {
  difference() {
    union() {
      difference() {
        cube([L,W,H]);
        translate([wall,wall,floor_t])
          cube([L-2*wall,W-2*wall,H]);
      }
      screw_positions() translate([0,0,floor_t]) cylinder(d=boss_d,h=boss_h);
    }
    screw_positions() translate([0,0,-0.1]) cylinder(d=screw_d,h=H+0.2);
    // Bukaan USB contoh; posisinya harus dicocokkan dengan board dan kabel.
    translate([-0.1,W/2-7,8]) cube([wall+0.2,14,10]);
    // Bukaan sensor pada dinding depan.
    translate([L-34,-0.1,8]) cube([24,wall+0.2,18]);
  }
}

module lid() {
  difference() {
    union() {
      cube([L,W,lid_t]);
      translate([wall+gap,wall+gap,lid_t]) difference() {
        cube([L-2*(wall+gap),W-2*(wall+gap),lip_h]);
        translate([lip_t,lip_t,-0.1])
          cube([L-2*(wall+gap+lip_t),W-2*(wall+gap+lip_t),lip_h+0.2]);
      }
    }
    screw_positions() translate([0,0,-0.1]) cylinder(d=screw_d,h=lid_t+lip_h+0.2);
    for (y = [20:6:44]) translate([65,y,-0.1]) cube([28,2,lid_t+0.2]);
    translate([97,62,-0.1]) cylinder(d=5.4,h=lid_t+0.2);
  }
}

if (part == "base") base();
if (part == "lid") lid();
if (part == "assembly") {
  base();
  translate([0,W,H+lid_t]) rotate([180,0,0]) lid();
}
