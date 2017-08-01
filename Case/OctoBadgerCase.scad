caseWidth = 110;
caseHeight = 45;
$fn=120;

module showModels() {
    // Our case is 110mm wide
    // dymo is 125 so hase 15mm overhand (7.5mm each side)
    // back Pi case to start 70mm in (at our y=0)
    // front RFID case to be about 50mm in front of the printer
    translate([-7.5,-70,caseHeight + 00]) {
        %labelWriter();
    }

    translate([(caseWidth - 56)/2, 35, 5]) {
        %raspberryPi();
    }

    translate([(caseWidth - 50)/2 + 50, -120+10, caseHeight-5]) {    
        rotate([0,180,0]) {
            %rfidPcb();
        }
    }
}

module raspberryPi() {
    
    // Rasberry Pi main body
    cube([56, 80, 30]); // 65mm + USB/Ethernet port.
    
    // USB Connections
    translate([56-35,-53,5]) {
        cube([35, 53, 30]);
    }
    
    translate([5,80,30]) {
        cube([12, 20, 20]);
    }
    
    // With connectors and supports.
    cube([56, 80, 45]);
    
    // 4 Pin power connector (connect printer power when running 24V into Pi Power Hat)
    translate([3,80-25,30]) {
        cube([12, 4, 20]);
    }
    
    // Holes.
    translate([0,80-65,-10]) {
        piScrewHoles(2.8);
    }
}

module piScrewHoles(d) {
h = 60;
    translate([3.5,3.5,0]) {
        cylinder(d=d,h=h);
    }
    translate([52.5,3.5,0]) {
        cylinder(d=d,h=h);
    }
    translate([52.5,61.5,0]) {
        cylinder(d=d,h=h);
    }
    translate([3.5,61.5,0]) {
        cylinder(d=d,h=h);
    }
}

module rfidPcb() {
    cube([50, 90, 18]);
    
    // USB Plug
    translate([33,90,6]) {
        cube([12, 50, 12]);
    }
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
                cube([40, 65, 20]);
            }
        }
    }
}

baseCutout = 65;
baseCutoutOffset = (caseWidth - baseCutout)/2;

module piCase() {
    
    
    // Front Section of the back half
    difference() {
        union() {
            cube([caseWidth, 60, caseHeight]);
        }
        union() {
            // Hollow the part below the printer
            translate([1.6,-1,1.6]) {
                cube([caseWidth-3.2, 62, caseHeight-3.2]);
            }
            
            // Base cutout for electronics insertion.
            translate([baseCutoutOffset,-0.1,-1]) {
                //cube([caseWidth- (2* baseCutoutOffset), 25, 5]);
            }
            
            // Put a curve in the top to help 
            translate([caseWidth/2,60,caseHeight-5]) {
                rotate([0,0,90]) {
                    cylinder(d=74, h=10);
                }
            }
            
            // This section overlaps with the back so ensure we have 
            // the screwholes set here as well.
            translate([(caseWidth - 56)/2,-10+60,-5]) {
                #piScrewHoles(3.6);
            }
        }
    }
    
    
    // Back section of the back half
    translate([0,60,0]) {
        difference() {
            union() {
                cube([caseWidth, 80, 80]);
            }
            union() {
                // Base cutout for electronics insertion.
                translate([10,-1,-1]) {
                    // Leave closed but add holes for Raspberry Pi mounting
                    //#cube([caseWidth-20, 20, 5]);
                }
                
                // Hollow the part below the printer
                translate([1.6,-0.1,1.6]) {
                    cube([caseWidth-3.2, 80-0.9, caseHeight-3.2]);
                }
                
                // Curve the end for the printer to sit into
                translate([-0.1,-5,caseHeight + 65]) {
                    rotate([0,90,0]) {
                        cylinder(d=130, h=caseWidth+0.2);
                    }
                }
                // Cut out the square recess for printer cabel
                translate([(caseWidth-74)/2,-1,caseHeight-2]) {
                    cube([74, 80, 34]);
                }
                
                // Hole for the power connector.
                powerHoleDiameter = 12.6;
                translate([caseWidth/2,82,40]) {
                    rotate([90,0,0]) {
                        cylinder(d=powerHoleDiameter, h=5);
                    }
                }
                
                translate([(caseWidth - 56)/2,-10,-5]) {
                    #piScrewHoles(3.6);
                }
            }
        }
    }
    
    // Add joint senction to help join to the rfid section
    translate([0,-15,0]) {
        difference() {
            union() {
                translate([1.6,0,1.6]) {
                    cube([caseWidth - 3.2, 25, caseHeight - 3.2]);
                }
            }
            union() {
                translate([3.2,-0.1,3.2]) {
                    cube([caseWidth - 6.4, 25.2, caseHeight - 6.4]);
                }
                
                translate([baseCutoutOffset,-0.1,0]) {
                    cube([caseWidth - (2 * baseCutoutOffset), 40.2, 4]);
                }
                
                // Add holes to allow the sections to be bolted together
                
                translate([10,7.5,-2]) {
                    #cylinder(d=3, h=caseHeight+10);
                }
                                
                translate([caseWidth/2,7.5,-2]) {
                    #cylinder(d=3, h=caseHeight+10);
                }
                
                translate([caseWidth-10,7.5,-2]) {
                    #cylinder(d=3, h=caseHeight+10);
                }
                
            }
        }
    }
    
        
    
}

module rfidCase() {   
    
    difference() {
        union() {
            cube([caseWidth, 150, caseHeight]);
        }
        union() {
            // Hollow the part below the printer
            translate([1.6,-0.1,1.6]) {
                cube([caseWidth-3.2, 152+5, caseHeight-3.2]);
            }
            
            // Base cutout for electronics insertion.
            translate([10,10,-1]) {
                cube([caseWidth-20, 151, 5]);
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


module landspeederEngineOutline(d) {
    hull() {
        cylinder(d=d-8, h=10);
        translate([0,0,30]) {
            cylinder(d=d-1, h=20);
        }
        translate([0,0,70]) {
            cylinder(d=d-8, h=10);
        }
    }
}
module landspeederEngine() {
    difference() {
        landspeederEngineOutline(caseHeight);
        translate([0,0,0]) {
            #landspeederEngineOutline(caseHeight-5);
        }
    }
}

color("blue") {
    //piCase();
    /*
    translate([-35, 60+80, 40]) {
        rotate([90,0,0]) {
            landspeederEngine();
        }
    }
    translate([caseWidth + 35, 60+80, 40]) {
        rotate([90,0,0]) {
            landspeederEngine();
        }
    }
    */
}

translate([0,-150,0]) {
    color("green") {
       rfidCase();
    }
}

showModels();