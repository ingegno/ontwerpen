// a filament cleaner to hold a sponge with cable ties

rotate([0,90,0])
difference() {
 rotate([0,90,0])
 difference() {
   translate([0,0,-10]) cylinder(r=8,h=20,$fn=50);
   translate([0,0,-9]) cylinder(r=7.,h=18,$fn=30);
   cylinder(r=3,h=30,$fn=30);
   translate([0,0,-30]) cylinder(r=1.6,h=30,$fn=30);
  //add two lines for cable ties  
  translate([0,0,5])
   rotate_extrude(convexity = 10)
    translate([9.5, 0, 0])
      circle(r = 2, $fn = 100);

  translate([0,0,-5])
   rotate_extrude(convexity = 10)
     translate([9.5, 0, 0])
     circle(r = 2, $fn = 100);
 };
 translate([-25,-25,-50]) cube([50,50,50]);
}
