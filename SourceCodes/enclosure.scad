// Portable Network Analyzer - enclosure, exploratory model.
//
// STATUS: geometry skeleton. Every value in the "Provisional" group comes from
// a ruler, a datasheet or an official drawing - NOT from the caliper. Connector
// cutouts are placeholders at invented coordinates. Nothing here is printable
// as a final part. Probe B at the bottom of this file is the exception: it
// depends only on verified constants and can be printed as is.

/* [What to render] */
part = "all"; // [all, tray, lid, probe_b]
show_placeholder_cuts = true;

/* [Verified constants] */
wall       = 2.4;   // shell thickness
divider_t  = 2.4;   // wall between board bay and battery bay
lid_t      = 2.4;
clr        = 1.5;   // clearance around a board
corner_r   = 4.0;
hole_fudge = 0.4;   // FDM holes come out undersized
cut_fudge  = 0.5;   // per side, connector cutouts
screw_d    = 2.5;   // M2.5
nut_af     = 5.0;   // M2.5 nut across flats
nut_h      = 2.0;
boss_d     = 8.0;
boss_embed = 1.0;   // bosses must overlap the wall, not touch it tangentially:
                    // zero-thickness contact breaks the mesh

/* [Provisional - replace after caliper] */
sandwich_l = 125.0; // ruler, 17.08.2026
sandwich_w = 90.0;  // ruler
sandwich_h = 25.0;  // ruler
ups_l      = 60.0;  // datasheet, module not bought
ups_w      = 93.0;  // datasheet
ups_h      = 25.0;  // datasheet
lcd_act_l  = 109.0; // computed from 5" diagonal at 800x480, not measured
lcd_act_w  = 65.0;  // same
bay_h      = 30.0;  // chosen, not derived

/* [Derived] */
bay1_x  = sandwich_l + 2 * clr;
bay2_x  = ups_l + 2 * clr;
inner_x = bay1_x + divider_t + bay2_x;
inner_y = max(sandwich_w, ups_w) + 2 * clr;
outer_x = inner_x + 2 * wall;
outer_y = inner_y + 2 * wall;
tray_h  = bay_h + wall;

boss_in  = wall + boss_d / 2 - boss_embed;
boss_pos = [
    [boss_in,           boss_in],
    [outer_x - boss_in, boss_in],
    [boss_in,           outer_y - boss_in],
    [outer_x - boss_in, outer_y - boss_in]
];

// [label, x from inner left, z from bay floor, width, height]
// TODO placeholders. Real coordinates come from block 5 of the measurement
// protocol, referenced to one corner of the Pi board.
front_cuts = [
    ["rj45",  12, 1, 16.0, 14.0],
    ["usb_ab", 34, 1, 15.5,  8.5],
    ["usb_cd", 56, 1, 15.5,  8.5]
];

module rbox(x, y, z, r) {
    hull()
        for (dx = [r, x - r], dy = [r, y - r])
            translate([dx, dy, 0]) cylinder(r = r, h = z, $fn = 48);
}

module bosses() {
    for (p = boss_pos)
        translate([p[0], p[1], wall]) cylinder(d = boss_d, h = bay_h, $fn = 32);
}

module boss_holes() {
    for (p = boss_pos) {
        translate([p[0], p[1], -1])
            cylinder(d = screw_d + hole_fudge, h = tray_h + 2, $fn = 32);
        translate([p[0], p[1], -0.01])
            cylinder(d = nut_af / cos(30), h = nut_h, $fn = 6);
    }
}

module divider() {
    // overlaps both side walls by 0.5 for the same reason as the bosses
    translate([wall + bay1_x, wall - 0.5, wall])
        cube([divider_t, inner_y + 1, bay_h]);
}

// Vents under the board bay: the SoC faces the display across a closed gap.
module vents() {
    n = 7; slot_w = 3.0; slot_l = 40.0; pitch = 9.0;
    for (i = [0 : n - 1])
        translate([wall + clr + 25 + i * pitch, outer_y / 2 - slot_l / 2, -1])
            cube([slot_w, slot_l, wall + 2]);
}

module front_cutouts() {
    for (c = front_cuts)
        translate([wall + c[1] - cut_fudge, -1, wall + c[2] - cut_fudge])
            cube([c[3] + 2 * cut_fudge, wall + 2, c[4] + 2 * cut_fudge]);
}

module tray() {
    difference() {
        union() {
            difference() {
                rbox(outer_x, outer_y, tray_h, corner_r);
                translate([wall, wall, wall])
                    rbox(inner_x, inner_y, tray_h, max(corner_r - wall, 0.1));
            }
            bosses();
            divider();
        }
        boss_holes();
        vents();
        if (show_placeholder_cuts) front_cutouts();
    }
}

module lid() {
    difference() {
        rbox(outer_x, outer_y, lid_t, corner_r);
        // TODO window is centred on the board bay. Real position depends on the
        // offset between the Pi board and the display board, not yet measured.
        translate([wall + clr + (sandwich_l - lcd_act_l) / 2,
                   (outer_y - lcd_act_w) / 2, -1])
            cube([lcd_act_l, lcd_act_w, lid_t + 2]);
        for (p = boss_pos)
            translate([p[0], p[1], -1])
                cylinder(d = screw_d + hole_fudge + 0.4, h = lid_t + 2, $fn = 32);
    }
}

// Probe B: pad, post, M2.5 clearance hole, captive nut pocket underneath.
// Depends only on verified constants. Printable as is.
module probe_b() {
    plate_x = 30; plate_y = 20; post_h = 6;
    difference() {
        union() {
            cube([plate_x, plate_y, wall]);
            translate([6, plate_y / 2, 0])
                cylinder(d = boss_d, h = post_h, $fn = 32);
        }
        translate([6, plate_y / 2, -1])
            cylinder(d = screw_d + hole_fudge, h = post_h + 2, $fn = 32);
        translate([6, plate_y / 2, -0.01])
            cylinder(d = nut_af / cos(30), h = nut_h, $fn = 6);
    }
}

if (part == "tray" || part == "all") tray();
if (part == "lid"  || part == "all") translate([0, 0, tray_h + 12]) lid();
if (part == "probe_b" || part == "all") translate([0, -35, 0]) probe_b();

// Printed to the console on every F5, so the resulting outer size is always
// visible without measuring the preview.
echo(str("outer  : ", outer_x, " x ", outer_y, " x ", tray_h + lid_t, " mm"));
echo(str("bay1   : ", bay1_x, " x ", inner_y, " x ", bay_h, " mm (boards)"));
echo(str("bay2   : ", bay2_x, " x ", inner_y, " x ", bay_h, " mm (battery)"));
