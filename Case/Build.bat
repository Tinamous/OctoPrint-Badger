@echo off

@echo Deleting old STL files.
del *.stl

@echo Building full case
"C:\Program Files\OpenSCAD\openscad.com" -o OctoBadgerCase-Full.stl -D "printRfidSection=true;printPiSection=true;printPiEngines=false" OctoBadgerCase.scad

@echo Building full case - with engines
"C:\Program Files\OpenSCAD\openscad.com" -o OctoBadgerCase-Full-WithEngines.stl -D "printRfidSection=true;printPiSection=true;printPiEngines=true" OctoBadgerCase.scad

@echo Building Front RFID sensor section
"C:\Program Files\OpenSCAD\openscad.com" -o OctoBadgerCase-Front.stl -D "printRfidSection=true;printPiSection=false;printPiEngines=false" OctoBadgerCase.scad

@echo Building Rear Pi section
"C:\Program Files\OpenSCAD\openscad.com" -o OctoBadgerCase-Rear.stl -D "printRfidSection=false;printPiSection=true;printPiEngines=false" OctoBadgerCase.scad

@echo Building Rear Pi section With Engines.
"C:\Program Files\OpenSCAD\openscad.com" -o OctoBadgerCase-Rear-WithEngines.stl -D "printRfidSection=false;printPiSection=true;printPiEngines=true" OctoBadgerCase.scad

