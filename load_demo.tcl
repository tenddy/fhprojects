
set auto_path [linsert $auto_path 0 "D:/Program Files/Spirent Communications/Spirent TestCenter 4.81/Spirent TestCenter Application"]
# puts $auto_path
package require SpirentTestCenter
# Create the root project object
# puts "Creating project ..."
# set hProject [stc::create project]

set configXml {E:\FHATP\fhprojects\instruments\config.xml}
stc::perform LoadFromXml -FileName $configXml

set hport [stc::get system1 -handle]
puts $hport
set hport [stc::get project1 -Handle]
puts $hport

set hportname [stc::get project1.port(2) -PortName]
puts $hportname


set info [stc::perform GetConfigInfo -QueryRoots project1]
puts $info
array set Arrayarg $info

puts $Arrayarg(-Names)
puts "####################"
# port
set hportTx [stc::get project1.port(1) -Handle]
puts $hportTx

set hportRx [stc::get project1.port(2) -Handle]
puts $hportRx
# Stream 
set hSteamBlockTx [stc::get $hportTx -Children-StreamBlock]
puts $hSteamBlockTx
foreach var $hSteamBlockTx {
    puts [stc::get $var -Name]
}
# device
    # hdevice

#