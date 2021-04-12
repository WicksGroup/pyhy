#!/bin/bash
#HyadesPostProcess FILENAME.inf PROPERTY
#User inputs the .inf file and the PROPERTY they are interested in
#Available properties:  R,U,Acc,Rho,Te,Ti,Tr,Pres,Zbar,Xmass,sd1

echo $1 > INPUT.$$
varName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1".dat" }')

if [ "$2" = "R" ]; then 
	awk 'BEGIN { print "i\n1\nn" }' >> INPUT.$$
	outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_R.dat" }')
elif [ "$2" = "U" ]; then
	awk 'BEGIN { print "i\n2\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_U.dat" }')
elif [ "$2" = "Acc" ]; then
        awk 'BEGIN { print "i\n3\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Acc.dat" }')
elif [ "$2" = "Rho" ]; then
        awk 'BEGIN { print "i\n4\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Rho.dat" }')
elif [ "$2" = "Te" ]; then
        awk 'BEGIN { print "i\n5\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Te.dat" }')
elif [ "$2" = "Ti" ]; then
        awk 'BEGIN { print "i\n6\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Ti.dat" }')
elif [ "$2" = "Tr" ]; then
        awk 'BEGIN { print "i\n7\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Tr.dat" }')
elif [ "$2" = "Pres" ]; then
        awk 'BEGIN { print "i\n8\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Pres.dat" }')
elif [ "$2" = "Zbar" ]; then
        awk 'BEGIN { print "i\n9\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Zbar.dat" }')
elif [ "$2" = "sd1" ]; then
        awk 'BEGIN { print "i\n10\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_sd1.dat" }')
elif [ "$2" = "Xmass" ]; then
        awk 'BEGIN { print "i\n11\nn" }' >> INPUT.$$
        outputvarName=$(echo $1 | sed 's/\.[^\.]*$//g' | awk '{ print $1"_Xmass.dat" }')
else
	echo No Match to available parameters
	echo Available properties:  R,U,Acc,Rho,Te,Ti,Tr,Pres,Zbar,Xmass,sd1
	exit 1
fi

hyadpost < INPUT.$$ > HYADOUT.$$

mv $varName $outputvarName

rm INPUT.$$ HYADOUT.$$
