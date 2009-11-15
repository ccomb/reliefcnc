# installation of the rail controller and alioscopy player
# on Ubuntu 9.04

# packages
sudo aptitude install vim mercurial python2.5 python2.5-dev python-setuptools ssh build-essential libusb-0.1-4 libusb-dev htop libavcodec52 vlc gstreamer0.10-ffmpeg gstreamer0.10-plugins-ugly nvidia-glx-180 libmp3lame0 flac mplayer mencoder libx264-65 git

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


# nvidia config
sudo nvidia-xconfig

# usb settings
sudo touch /etc/udev/rules.d/75-soprolec.rules
sudo chmod 777 /etc/udev/rules.d/75-soprolec.rules
cat > /etc/udev/rules.d/75-soprolec.rules << EOF
SYSFS{idVendor}=="067b", SYSFS{idProduct}=="2303", MODE="777"
EOF
sudo chmod 644 /etc/udev/rules.d/75-soprolec.rules

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
mkdir -p relief
cd relief
hg clone https://ccomb:antalya@cody.gorfou.fr/hg/pycnic
hg clone https://ccomb:antalya@cody.gorfou.fr/hg-private/reliefcnc
hg clone https://ccomb:antalya@cody.gorfou.fr/hg-private/reliefgui

# dependencies
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


