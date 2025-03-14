
## ------------------ script-psqt5.sh ---------------------
##  Takes care of the usual suspects - required 
##  Cleans up comments, code and tokens in videoplayer files
## -------------------------------------------------------

sed -i -- 's/PyQt6/PyQt5/g' *.py
sed -i -- 's/e.globalPosition()/e.globalPos()/g' *.py
sed -i -- 's/e.position()/e.pos()/g' *.py

python3 ./script-qt5.py

rm *.py--
