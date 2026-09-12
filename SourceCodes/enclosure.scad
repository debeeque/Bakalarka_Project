// Portable Network Analyzer - enclosure, exploratory model.
//
// STATUS: geometry skeleton. Values in the "Provisional" group come from a
// ruler, a datasheet or an official drawing - NOT from the caliper. Panel
// feature positions are a design proposal, not measurements. Nothing here is
// printable as a final part except probe_b, which depends only on verified
// constants.
//
// Panel layout follows the decision recorded in _context/05_akum_korpus.md:
// both USB/LAN dongles stay inside and are patched to three keystone RJ45
// jacks on the panel. Nothing outside has to line up with the Pi's own USB or
// Ethernet connectors. Only three things are dictated by the hardware - the
// microSD slot, the display window and the display mounting holes.

/* [What to render] */
part = "all"; // [all, tray, lid, probe_b]

/* [Verified constants] */
wall       = 2.4;
divider_t  = 2.4;
lid_t      = 2.4;
clr        = 1.5;
corner_r   = 4.0;
hole_fudge = 0.4;   // FDM holes come out undersized
cut_fudge  = 0.5;   // per side, panel cutouts
screw_d    = 2.5;   // M2.5
nut_af     = 5.0;   // M2.5 nut across flats
nut_h      = 2.0;
boss_d     = 8.0;
boss_embed = 1.0;   // bosses overlap the wall; tangential contact breaks the mesh

/* [Provisional - replace after caliper] */
sandwich_l = 125.0; // ruler, 17.08.2026, includes protruding parts
sandwich_w = 90.0;  // ruler
ups_l      = 60.0;  // datasheet, module not bought
ups_w      = 93.0;  // datasheet
lcd_act_l  = 109.0; // computed from 5" diagonal at 800x480, not measured
lcd_act_w  = 65.0;  // same
bay_h      = 30.0;  // chosen, not derived

/* [Panel features - sizes need the real parts, positions are a proposal] */
keystone_w     = 14.5;  // standard snap-in opening; verify on the real jack
keystone_h     = 16.0;
keystone_n     = 3;
keystone_pitch = 22.0;
keystone_x0    = 20.0;  // from the inner left of the board bay
keystone_z     = 5.0;   // above the bay floor
dc_jack_d      = 8.0;   // DC5521 panel mount barrel; verify
switch_w       = 13.0;  // panel switch window; verify
switch_h       = 8.0;
sd_slot_w      = 16.0;  // TODO caliper: microSD protrusion plus clearance
sd_slot_h      = 3.5;
sd_slot_y      = 28.0;  // TODO caliper: position of the card along the Pi edge
sd_slot_z      = 4.0;

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

// Front wall: three keystone jacks over the board bay, plus the backlight
// switch. The backlight slider sits on the display board and is unreachable
// once the case is closed, so it is wired out to this switch.
module front_panel() {
    for (i = [0 : keystone_n - 1])
        translate([wall + keystone_x0 + i * keystone_pitch - cut_fudge, -1,
                   wall + keystone_z - cut_fudge])
            cube([keystone_w + 2 * cut_fudge, wall + 2, keystone_h + 2 * cut_fudge]);
    translate([wall + bay1_x - 30, -1, wall + keystone_z + 2])
        cube([switch_w, wall + 2, switch_h]);
}

// Battery end wall: charging jack and main power switch.
module battery_end() {
    translate([outer_x - wall - 1, wall + inner_y * 0.35, wall + 14])
        rotate([0, 90, 0]) cylinder(d = dc_jack_d + hole_fudge, h = wall + 2, $fn = 32);
    translate([outer_x - wall - 1, wall + inner_y * 0.62 - switch_w / 2,
               wall + 14 - switch_h / 2])
        cube([wall + 2, switch_w, switch_h]);
}

// Board end wall: slot for the microSD card, which protrudes past the Pi.
// The card sits on the Pi edge opposite USB and Ethernet, so the sandwich must
// be oriented with that edge toward this wall - otherwise the card ends up
// facing the divider and cannot be pulled out at all.
module sd_slot() {
    translate([-1, wall + sd_slot_y - sd_slot_w / 2, wall + sd_slot_z])
        cube([wall + 2, sd_slot_w, sd_slot_h]);
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
        front_panel();
        battery_end();
        sd_slot();
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

echo(str("outer  : ", outer_x, " x ", outer_y, " x ", tray_h + lid_t, " mm"));
echo(str("bay1   : ", bay1_x, " x ", inner_y, " x ", bay_h, " mm (boards)"));
echo(str("bay2   : ", bay2_x, " x ", inner_y, " x ", bay_h, " mm (battery)"));
