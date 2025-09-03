
## ------------------- script-ps6.sh ----------------------
##  Cleans up comments, code and tokens in videoplayer files
##  Takes care of the usual suspects - required 
#   Replaces 'type' with 'desc' for description in code and .play files
## -------------------------------------------------------

python3  ./script-qt6.py  ## does the clean up

sed -i -- 's/PyQt6/PySide6/g' *.py
sed -i -- 's/pyqtSlot/Slot/g' *.py
sed -i -- 's/pyqtSignal/Signal/g' *.py
sed -i -- 's/pyqtProperty/Property/g' *.py

sed -i -- 's/pix.type /pix.desc /g' *.py
sed -i -- 's/bkg.type /bkg.desc /g' *.py
sed -i -- 's/self.type /self.desc /g' *.py
sed -i -- 's/self.bkgItem.type /self.bkgItem.desc /g' *.py
sed -i -- 's/itm.type /itm.desc /g' *.py

sed -i -- 's/flat.type /flat.desc /g' *.py
sed -i -- 's/p.type /p.desc /g' *.py
sed -i -- 's/ptr.type /ptr.desc /g' *.py
sed -i -- 's/typ.type /typ.desc /g' *.py
sed -i -- 's/pix.type\:/pix.desc\:/g' *.py
sed -i -- 's/itm.type\./itm.desc\./g' *.py

sed -i -- 's/line.type /line.desc /g' *.py
sed -i -- 's/typ.type /typ.desc /g' *.py
sed -i -- "s/\[\'type\'\]/\[\'desc\'\]/g" *.py
sed -i -- "s/\'type\'/\'desc\'/g" *.py
sed -i -- "s/typ\.type\:/typ\.desc\:/g" *.py

rm *.py--

cd ../plays 

sed -i -- "s/type/desc/g" *.play

rm *.play--

