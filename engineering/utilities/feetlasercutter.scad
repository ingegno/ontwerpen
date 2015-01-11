// feet for the lasercutter platform

difference() {
   cylinder(r=10,h=18,$fn=50);
   translate([0,0,5]) cube([20,20,20]);
}