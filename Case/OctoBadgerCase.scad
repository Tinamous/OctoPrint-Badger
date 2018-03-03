caseWidth = 140; // Was 110 but label writer sticks out 10mm on each side 
caseHeight = 50; //45
$fn=120;

//rfidCaseLength = 125;
rfidCaseLength = 113;
wallWidth = 2;
// Allow for the join esction lip.
piCaseWallWidth = wallWidth + 0.2;

//printAllAtOnce = true;
printRfidSection = true;
printPiSection = true;
printPiEngines = true;
// If printing both at the same time then
// don't bother with the joing section and holes.
printAllAtOnce = printRfidSection && printPiSection;

includeSideButtons = true;
switchCutoutDiameter = 29;

includeUsbHole = false;

module showModels() {
    // Our case is 110mm wide
    // dymo is 125 so hase 15mm overhand (7.5mm each side)
    // back Pi case to start 70mm in (at our y=0)
    // front RFID case to be about 50mm in front of the printer
    translate([(caseWidth - 125)/2,-65,caseHeight + 00]) {
        //%labelWriter();
    }

    if (printPiSection) {
        // Place the Pi dead centeral.
        translate([(caseWidth - 56)/2, 35, 5]) {
            %raspberryPi();
        }
    }

    if (printRfidSection) {        
        translate([(caseWidth - 57)/2, -rfidCaseLength -3, caseHeight-20]) {    
          //  %rfidModule();
        }
    }
}

// Show a model of the Raspberry Pi to check sizing
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
h = 40;
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

// Show a model of the RFID module to check sizing
module rfidModule() {
    cube([57, 97, 18]);
    
    // Hidhlight the rfid area
    // aerial 57mm diameter, 3mm offset from case edge + 5mm from pcb
    translate([57/2,57/2+5,10]) {
        cylinder(d=50, h=20);
    }

    
    // USB Plug
    translate([5,90,6]) {
        #cube([12, 50, 12]);
    }
    
    // Centered.
    //translate([(caseWidth - 50)/2 + 50, -140+10, caseHeight-5]) {    
        
    // Holes 90mm appart
    // rfid case is 57mm.
    translate([-(90-57)/2, 10, 0]) {    
        rfidScrewHoles(3.2);
    }
}

// Holes in rfid case 90 x 60mm appart.
module rfidScrewHoles(d) {
    
h=60;
    translate([0,0,0]) {
        cylinder(d=d,h=h);
    }
    translate([90,0,0]) {
        cylinder(d=d,h=h);
    }
    translate([0,55,0]) {
        cylinder(d=d,h=h);
    }
    translate([90,55,0]) {
        cylinder(d=d,h=h);
    }
}

module rfidScrewHolesCountersunk(d) {
    
h=wallWidth+0.2;
d2 = 6.5; // M3 countsunk head size
    translate([0,0,0]) {
        cylinder(d1=d,d2=d2, h=h);
    }
    translate([90,0,0]) {
        cylinder(d1=d,d2=d2,h=h);
    }
    translate([0,55,0]) {
        cylinder(d1=d,d2=d2,h=h);
    }
    translate([90,55,0]) {
        cylinder(d1=d,d2=d2,h=h);
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

baseCutout = 100;
baseCutoutOffset = (caseWidth - baseCutout)/2;

// Rear half of the case containing the Raspberry
// Pi.
module piCase() {
    
    
    // Front Section of the back half
    difference() {
        union() {
            cube([caseWidth, 60, caseHeight]);
        }
        union() {
            // Hollow the part below the printer
            translate([piCaseWallWidth,-1,piCaseWallWidth]) {
                cube([caseWidth-(piCaseWallWidth*2), 62, caseHeight-(piCaseWallWidth*2)]);
            }
                        
            // Put a curve in the top to help 
            translate([caseWidth/2,60,caseHeight-5]) {
                rotate([0,0,90]) {
                    cylinder(d=74, h=10);
                }
            }
            
            // This section overlaps with the back so ensure we have 
            // the screwholes set here as well.
            translate([(caseWidth - 56)/2,60 - 10,-5]) {
                #piScrewHoles(3.6);
            }
        }
    }
    
    
    // Back section of the back half
    translate([0,60,0]) {
        difference() {
            union() {
                cube([caseWidth, 80, 35 + caseHeight]);
            }
            union() {               
                // Hollow the part below the printer
                translate([piCaseWallWidth,-0.1,piCaseWallWidth]) {
                    cube([caseWidth-(piCaseWallWidth*2), 80-0.9, caseHeight-(piCaseWallWidth*2)]);
                }
                
                // Curve the end for the printer to sit into
                translate([-0.1,-5,caseHeight + 65]) {
                    rotate([0,90,0]) {
                        cylinder(d=130, h=caseWidth+0.2);
                    }
                }
                
                // Cut out the square recess for printer cable
                translate([(caseWidth-74)/2,-1,caseHeight-(piCaseWallWidth+1)]) {
                    cube([74, 80, 38 - piCaseWallWidth]);
                }
                
                // Repeat cutout but to include part of the top section as well.
                translate([(caseWidth-74)/2,-1,caseHeight-2]) {
                    cube([74, 54 + 9, 40]);
                }
                
                // Hole for the power connector.
                powerHoleDiameter = 12.6;
                //translate([caseWidth/2,82,70]) {
                translate([15+9,82,10 + 5]) {
                    rotate([90,0,0]) {
                        cylinder(d=powerHoleDiameter, h=5);
                    }
                }
                
                // Hole for USB lead for Pi.
                if (includeUsbHole) {
                    translate([15,75,25]) {
                            #cube([18, 10, 10]);
                    }
                }
                
                // Holes for Raspberry Pi.
                translate([(caseWidth - 56)/2,-10,-5]) {
                    piScrewHoles(3.6);
                }
            }
        }
    }
    
    if (!printAllAtOnce) {
        // Add joint senction to help join to the rfid section
        difference() {
            union() {           
                // Use RFID wall width (smaller than this)
                // to align the joint section with the rfid case
                
                translate([wallWidth+0.1,-15,wallWidth+0.1]) {
                    // wallWidth is wall width
                    // so 0.1mm smaller all around
                    //cube([caseWidth - 3.6, 25, caseHeight - 3.6]);
                }
                
                translate([5,-15, wallWidth+0.1]) {
                    #cube([caseWidth-10, 25,1.6]);
                    translate([0,0,1.6/2]) {
                        rotate([0,90,0]) {
                            cylinder(d=3, h=caseWidth-10);
                        }
                    }
                }
                
                // 2mm thick so drop down 2.1mm for thickness
                // + fitting tollerance.
                translate([5,-15,caseHeight - (wallWidth+1.7)]) {
                    #cube([caseWidth-10, 25,1.6]);
                    translate([0,0,1.6/2]) {
                        rotate([0,90,0]) {
                            cylinder(d=3, h=caseWidth-10);
                        }
                    }
                }
                
                // Side parts for bolts.
                translate([wallWidth+0.1,-15,(caseHeight/2)-10]) {
                    cube([2, 25,20]);
                }
                
                translate([caseWidth - (wallWidth+0.1+2),-15,(caseHeight/2)-10]) {
                    cube([2, 25,20]);
                }
                
                // TODO: Add M4 Cylinder to top/bottom for latching.
            }
            union() {
                translate([0,-15.001,0]) {                
                    translate([baseCutoutOffset,-0.1,0]) {
                        //#cube([caseWidth - (2 * baseCutoutOffset), 40.2, 4]);
                    }
                    
                    // Add holes to allow the sections to be bolted together
                    // Left
                    translate([10,7.5,-2]) {
                        cylinder(d=3.5, h=caseHeight+10);
                    }
                    
                    // Across the width                
                    translate([-10,7.5,caseHeight/2]) {
                        rotate([0,90,0]) {
                            #cylinder(d=3.5, h=caseWidth+20);
                        }
                    }
                    // Right
                    translate([caseWidth-10,7.5,-2]) {
                        #cylinder(d=3, h=caseHeight+10);
                    }
                }
            }
        }     
    }
    
    // Add some text to the back behind the printer
    translate([6,140-17,35 + caseHeight-0.1]) {
        linear_extrude(2) {
            text("Do Not Hack", size=16);
        }
    }
}

module printerFrontArc() {
    // Arc radius is 75mm.
    difference() {
        union() {
            cylinder(r=80, h=4);
        }
        union() {
            translate([0,0,-0.01]) {
                cylinder(r=75, h=4.1);
                // And cut off anything back from 15ish mm...
                translate([-80,-65,0]) {
                    cube([80*2, 80*2, 4.5]);
                }
            }
        }
    }
}


// Cutouts in left and right side for
// pinball table style LEDs switches.
module switchCutouts() {    
    translate([-2, 35, caseHeight/2]) {
        rotate([0,90,0]) {
            #cylinder(d=switchCutoutDiameter, h=caseWidth + 4);
        }
    }
}

// Front half of the case that contains the
// RFID reader and bittons.
module rfidCase() {   
    
    difference() {
        union() {
            cube([caseWidth, rfidCaseLength , caseHeight]);
            // Arc front inner is 75mm from the arc center
            // so the arc center is 75mm back from the point
            // that the arc center should be at.
            translate([caseWidth/2,rfidCaseLength  - (41-75 +2),caseHeight]) {
                printerFrontArc();
            }
        }
        union() {
            // Hollow the part below the printer
            translate([wallWidth,-0.1,wallWidth]) {
                cube([caseWidth-(wallWidth*2), rfidCaseLength +5, caseHeight-(wallWidth*2)]);
            }
            
            // Base cutout for electronics insertion.
            // AND to get to the nuts/bots
            translate([baseCutoutOffset,10,-1]) {
                cube([baseCutout, rfidCaseLength-10-20, 5]);
            }
            
            if (!printAllAtOnce) {
                // Add holes to allow the sections to be bolted together
                translate([0,rfidCaseLength - 15,0]) {
                    translate([10,7.5,-2]) {
                        cylinder(d=3.5, h=caseHeight+10);
                    }
                                    
                    // Across the width                
                    translate([-10,7.5,caseHeight/2]) {
                        rotate([0,90,0]) {
                            cylinder(d=3.5, h=caseWidth+20);
                        }
                    }
                    
                    translate([caseWidth-10,7.5,-2]) {
                        cylinder(d=3.5, h=caseHeight+10);
                    }
                }
                
                // Recesses for the mating cylinders to sit into.
                // Bottom
                translate([4,rfidCaseLength-15,wallWidth + (1.8/2)]) {
                    rotate([0,90,0]) {
                        cylinder(d=3.1, h=caseWidth-8);
                    }
                }
                
                // Top
                translate([4,rfidCaseLength-15,caseHeight-(wallWidth + (1.8/2))]) {
                    rotate([0,90,0]) {
                        cylinder(d=3.1, h=caseWidth-8);
                    }
                }
            }

            // Holes for the RFID mounting case.
            // 90mm between centers on x
            translate([(caseWidth - 90)/2, 7, caseHeight - wallWidth-0.1]) {
                // 3.5mm works well for M3 bolts.
                //rfidScrewHoles(3.5);
                rfidScrewHolesCountersunk(3);
            }
            
            // Very small dent in the case
            // to highliht the position of the sensor.
            translate([caseWidth/2, 34, caseHeight-0.4]) {
                //cylinder(d=50, h=2);
            }
        }
    }
    
    // Rounded Nose
    addRoundedNode();
}

module addRoundedNode() {
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
                    translate([wallWidth,0,0]) {
                        rotate([0,90,-0]) {
                            cylinder(d=caseHeight-(wallWidth*2), h=caseWidth - (wallWidth*2));
                        }
                        translate([0,1,-(caseHeight/2)-2]) {
                            cube([caseWidth-(wallWidth*2),caseHeight/2+5,caseHeight+4]);
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
            landspeederEngineOutline(caseHeight-5);
        }
    }
}

if (printPiSection) {
    color("blue") {
        piCase();
        
        // Add "engines" to the side.
        if (printPiEngines) {
            translate([-35, 60+80, 40]) {
                rotate([90,0,0]) {
                    landspeederEngine();
                }
                translate([22,-50,-5]) {
                    cube([14,20,10]);
                }
            }
            translate([caseWidth + 35, 60+80, 40]) {
                rotate([90,0,0]) {
                    landspeederEngine();
                }
                translate([-38,-50,-5]) {
                    cube([14,20,10]);
                }
            }
        }
    }
}

if (printRfidSection) {
    translate([0,-rfidCaseLength,0]) {
        color("green") {
            difference() {
                union() {
                    rfidCase();
                }
                union() {
                    // Addd holes in the sides for switches
                    // pinball machine style :-)
                    if (includeSideButtons) {
                        switchCutouts();
                    }
                }
            }
        }
    }
}

showModels();