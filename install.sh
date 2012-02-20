# installation of the rail controller and alioscopy player
# on Ubuntu 9.04

# packages
sudo aptitude install vim mercurial python2.5 python2.5-dev python-setuptools ssh build-essential libusb-0.1-4 libusb-dev htop libavcodec52 vlc gstreamer0.10-ffmpeg gstreamer0.10-plugins-ugly libmp3lame0 flac mplayer mencoder libx264-65 git libltdl7 libltdl-dev libexif12 libexif-dev libpopt0 libpopt-dev libreadline6 libreadline6-dev

# ffmpeg and libx264
sudo aptitude install subversion git-core checkinstall yasm texi2html libfaac-dev libfaad-dev libmp3lame-dev libsdl1.2-dev libtheora-dev libx11-dev libxvidcore4-dev zlib1g-dev
sudo aptitude remove ffmpeg x264
# x264
cd
git clone git://git.videolan.org/x264.git
cd x264
./configure
make
sudo checkinstall --fstrans=no --install=yes --pkgname=x264 --pkgversion "1:0.svn`date +%Y%m%d`-0.0ubuntu1" --default
# ffmpeg
cd
svn checkout svn://svn.ffmpeg.org/ffmpeg/trunk ffmpeg
cd ffmpeg
./configure --enable-gpl --enable-nonfree --enable-pthreads --enable-libfaac --enable-libfaad --enable-libmp3lame --enable-libtheora --enable-libx264 --enable-libxvid --enable-x11grab
make
sudo checkinstall --fstrans=no --install=yes --pkgname=ffmpeg --pkgversion "3:0.svn`date +%Y%m%d`-12ubuntu3" --default


# usb settings
#sudo touch /etc/udev/rules.d/75-soprolec.rules
#sudo chmod 777 /etc/udev/rules.d/75-soprolec.rules
#cat > /etc/udev/rules.d/75-soprolec.rules << EOF
#SYSFS{idVendor}=="067b", SYSFS{idProduct}=="2303", MODE="777"
#EOF
#sudo chmod 644 /etc/udev/rules.d/75-soprolec.rules

# vim settings
cat > ~/.vimrc << EOF
set laststatus=2
set textwidth=80
set expandtab
set softtabstop=4
set sw=4
:syntax on
:filetype plugin on
set foldmethod=indent
set foldlevel=1
set tabstop=2
autocmd FileType python autocmd BufWritePre * :%s/\s\+$//e
autocmd BufReadPost * if line("'\"") > 0 && line("'\"") <= line ("$") | exe "normal g'\"" | endif
map <F7> o>>> import interlude; interlude.interact(locals())<Esc>
imap xxx import pdb; pdb.set_trace()
EOF

# mercurial settings
cat > ~/.hgrc << EOF
[ui]
username = Christophe Combelles <ccomb@free.fr>

[extensions]
hgext.mq = 
hgext.graphlog = 
EOF

# buildout settings

mkdir ~/.buildout
cat > ~/.buildout/default.cfg << EOF
[buildout]
eggs-directory = /home/ccomb/buildout-eggs
EOF

# application code
cd
mkdir -p relief
cd relief
hg clone https://bitbucket.org/ccomb/pycnic
hg clone https://bitbucket.org/ccomb/reliefcnc
hg clone https://bitbucket.org/ccomb/reliefgui

# pyusb
wget -c http://downloads.sourceforge.net/project/pyusb/pyusb/0.4.2/pyusb-0.4.2.tar.gz?use_mirror=freefr
tar xzf pyusb-0.4.2.tar.gz
ln -s pyusb-0.4.2 pyusb

# build
for i in pycnic reliefcnc reliefgui; do
  cd ${i}
  hg pull -u
  python2.5 bootstrap.py
  ./bin/buildout
  cd ..
done

#libgphoto2
cd
wget http://downloads.sourceforge.net/project/gphoto/libgphoto/2.4.7/libgphoto2-2.4.7.tar.bz2?use_mirror=freefr
tar xjf libgphoto2-2.4.7.tar.bz2
cd libgphoto2-2.4.7
./configure
make
sudo checkinstall --fstrans=no --install=yes --pkgname=libgphoto2 --pkgversion "2.4.7-relief1" --default

# gphoto2
cd
wget http://downloads.sourceforge.net/project/gphoto/gphoto/2.4.7/gphoto2-2.4.7.tar.bz2?use_mirror=freefr
tar xjf gphoto2-2.4.7.tar.bz2
cd gphoto2-2.4.7
# patch
cat > /tmp/patch << EOF
632a633
>   if (glob_interval != -1 || frames != 1) {
706a708
>    }
EOF
patch -p0 gphoto2/main.c < /tmp/patch
rm /tmp/patch
./configure
make
sudo checkinstall --fstrans=no --install=yes --pkgname=gphoto2 --pkgversion "2.4.7-relief1" --default

# enable dnsmasq (dhcp+dns for local use)
sudo aptitude install dnsmasq
# remove dhcp config
sudo sed -i '/^dhcp-range=.*/d' /etc/dnsmasq.conf
# add dhcp config
sudo sed -i '$adhcp-range=10.0.0.2,10.0.0.50,255.255.255.0,12h' /etc/dnsmasq.conf

# remove ourselves
sudo sed -i '/^10.0.0.1.*/d' /etc/hosts
# append ourselves
sudo sed -i '$a10.0.0.1 relief' /etc/hosts


# don't login automatically
sudo sed -i 's/AutomaticLoginEnable=true/AutomaticLoginEnable=false/' /etc/gdm/custom.conf

# start the reliefgui automatically
sudo sed -i '/#relief/d' /etc/rc.local
sudo sed -i "/^exit/isu - ccomb -c 'cd /home/ccomb/relief/reliefgui; ./bin/paster serve --daemon development.ini' #relief" /etc/rc.local

# nm config
cat > /tmp/relief << EOF
[connection]
id=relief
uuid=286a944a-8443-4b8e-acbc-dc2da66637ca
type=802-3-ethernet
autoconnect=true
timestamp=0

[ipv4]
method=manual
addresses1=10.0.0.1;24;10.0.0.1;
ignore-auto-routes=false
ignore-auto-dns=false
dhcp-send-hostname=false
never-default=false

[802-3-ethernet]
speed=0
duplex=full
auto-negotiate=true
mac-address=0:1c:c0:9c:2a:85
mtu=0

[ipv6]
method=ignore
ignore-auto-routes=false
ignore-auto-dns=false
never-default=false
EOF
sudo mv /tmp/relief /etc/NetworkManager/system-connections/relief

# net config
macaddr=`/sbin/ifconfig eth2|grep HW|awk '{print $5}'`
sudo sed -i "/^no-auto-default=/d" /etc/NetworkManager/nm-system-settings.conf
sudo sed -i "/^\[main\].*/ano-auto-default=$macaddr," /etc/NetworkManager/nm-system-settings.conf

cat > /tmp/interfaces << EOF
auto lo eth2
iface lo inet loopback

iface eth2 inet static
address 10.0.0.1
netmask 255.255.255.0
gateway 10.0.0.1
EOF
sudo mv /tmp/interfaces /etc/network/interfaces
