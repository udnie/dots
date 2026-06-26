
## ------------------- script-ps6.sh ----------------------
##  Cleans up comments, code and tokens in videoplayer files
##  Takes care of the usual suspects - required 
#   Replaces 'type' with 'desc' for description in code and .play files
## -------------------------------------------------------

sed -i -- 's/PyQt6/PySide6/g' *.py
sed -i -- 's/pyqtSlot/Slot/g' *.py
sed -i -- 's/pyqtSignal/Signal/g' *.py
sed -i -- 's/pyqtProperty/Property/g' *.py

python3  ./script-qt6.py  ## does the clean up

rm *.py--

