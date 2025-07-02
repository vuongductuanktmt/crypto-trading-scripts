# Clone the updated TA-Lib repository
git clone https://github.com/TA-Lib/ta-lib.git ~/ta-lib
cd ~/ta-lib

# Install build tools (if missing)
sudo apt install automake autoconf libtool -y

# Generate the configure script
chmod +x autogen.sh
./autogen.sh

# Compile and install
./configure --prefix=/usr
make -j4
sudo make install
sudo ldconfig  # Update library cache

# Uninstall existing Python wrapper
pip3 uninstall TA-Lib -y

# Reinstall with correct paths
CFLAGS="-I/usr/include" LDFLAGS="-L/usr/lib" pip3 install --no-cache-dir TA-Lib

# If this is giving version number it means everythig is ok
python3 -c "import talib; print(talib.__version__)"
