caseWidth = 110;
caseHeight = 30;
$fn=60;

module raspberryPi() {
}

module rfidPcb() {
}
    

module labelWriter() {
    difference() {
        union() {
            cube([125, 185, 140]);
        }
        union(){ 
            translate([(125 - 55)/2, 125 ,-0.1]) {
                cube([55, 45, 20]);
            }
            translate([(125 - 40)/2, 125 ,-0.1]) {
                #cube([40, 65, 20]);
            }
        }
    }
}


module piCase() {
    
    /*
    // Front Section of the back half
    difference() {
        union() {
            cube([caseWidth, 60, 30]);
        }
        union() {
            // Hollow the part below the printer
            translate([1.6,-1,1.6]) {
                cube([caseWidth-3.2, 62, 30-3.2]);
            }
            
            // Base cutout for electronics insertion.
            translate([10,-1,-1]) {
                cube([caseWidth-20, 62, 5]);
            }
        }
    }
    */
    
    // Back section of the back half
    translate([0,60,0]) {
        difference() {
            union() {
                cube([caseWidth, 80, 80]);
            }
            union() {
                // Base cutout for electronics insertion.
                translate([10,-1,-1]) {
                    cube([caseWidth-20, 80-11.6, 5]);
                }
                
                // Hollow the part below the printer
                translate([1.6,-0.1,1.6]) {
                    cube([caseWidth-3.2, 80-1.61, 30-3.2]);
                }
                
                // Curve the end for the printer to sit into
                translate([-0.1,-5,caseHeight + 65]) {
                    rotate([0,90,0]) {
                        cylinder(d=130, h=caseWidth+0.2);
                    }
                }
                // Cut out the square recess for printer cabel
                translate([(caseWidth-74)/2,-1,caseHeight-2]) {
                   # cube([74, 80, 48]);
                }
                
                // Hole for the power connector.
                powerHoleDiameter = 12.6;
                translate([caseWidth/2,82,40]) {
                    rotate([90,0,0]) {
                        cylinder(d=powerHoleDiameter, h=5);
                    }
                }
            }
        }
    }
    
        
    
}

module rfidCase() {   
    
    difference() {
        union() {
            cube([caseWidth, 120, 30]);
        }
        union() {
            // Hollow the part below the printer
            translate([1.6,-0.1,1.6]) {
                cube([caseWidth-3.2, 122+5, 30-3.2]);
            }
            
            // Base cutout for electronics insertion.
            translate([10,10,-1]) {
                cube([caseWidth-20, 111, 5]);
            }
        }
    }
    
    translate([0,00,0]) {
    
    // Give it a rounded nose to make it look better
    // and to help print so it can be printed vertically.
    translate([0,0,caseHeight/2]) {
        difference() {
            union() {
                rotate([0,90,-0]) {
                    cylinder(d=caseHeight, h=caseWidth);
                }
            }
            union() {
                translate([1.6,0,0]) {
                    rotate([0,90,-0]) {
                        cylinder(d=caseHeight-3.2, h=caseWidth - 3.2);
                    }
                    translate([0,-2,-(caseHeight/2)+1.6]) {
                        cube([caseWidth-3.2,caseHeight/2+5,caseHeight-3.2]);
                    }
                }
            }
        }
    }
}
}

color("blue") {
    piCase();
}

translate([0,-120,0]) {
    color("green") {
        //rfidCase();
    }
}

// Our case is 110mm wide
// dymo is 125 so hase 15mm overhand (7.5mm each side)
// back Pi case to start 70mm in (at our y=0)
// front RFID case to be about 50mm in front of the printer
translate([-7.5,-70,caseHeight + 00]) {
    %labelWriter();
    %raspberryPi();
    %rfidPcb();
}