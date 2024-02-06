@echo off
sed s/_%outputsuffix%//g <%2 >%2.fordiff.txt
python colourdiff.py %1 %2.fordiff.txt 