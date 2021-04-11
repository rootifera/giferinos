# Giferinos 

An ffmpeg gif generator wrapper written in python

## Description

The purpose of Giferinos is to generate gifs from video files. It uses ffmpeg directly to achieve that. 

If your source folder has multiple video files they will be processed one by one. If the videos under
your source folder are in separate subfolders you will have the exact same folder hierarchy in the destination folder. 

### Disclaimer

Use it at your own risk. I'm not responsible of any of the damage this script may cause.  
<em>(Although I would like to know how you managed to damage something with this script, would be a fun story to listen)</em>

### Installing

There is no installation. Script runs just like any other python script. Since the script uses ffmpeg directly 
you need ffmpeg installed in your system before running this script.

I tested the script with Ubuntu 20.04 running under Windows 10 WSL and directly under Windows 10. 

* Linux:

```
sudo apt-get install ffmpeg                      # or whatever your distro has for installing packages.
git clone https://github.com/rootifera/giferinos.git
cd giferinos
pip install -r requirements.txt
```

* Windows:

Install ffmpeg for Windows:
https://ffmpeg.org/download.html

```
pip install python-magic-win64 python-magic-bin
git clone https://github.com/rootifera/giferinos.git
```

### Executing program

* Linux:

If you want to use defaults run the following. 
```
~/giferinos$ ./giferinos.py --source=/path/to/videos/ --destination=/where/to/save/gifs/
```

* Windows:

Just like Linux the most basic way is giving source and destination folders. Only difference is the way we enter path. 

```
C:\giferinos-main> python giferinos.py --source=C:\\path\\to\\videos\\ --destination=D:\\where\\to\\save\\gifs\\
```

There are few more options you can use to customize your gifs. 

```
usage: giferinos.py [-h] [-s SOURCE] [-d DESTINATION] [-l LENGTH] [-b BEGIN] [-r1 RANDSTART] [-r2 RANDEND]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        source videos full path (recursive)
  -d DESTINATION, --destination DESTINATION
                        location to save gifs (each video creates a folder same name as the video)
  -l LENGTH, --length LENGTH
                        gif length in seconds (default 4.3s)
  -b BEGIN, --begin BEGIN
                        gif generation starts from this value. Good for skipping intros(in seconds, default 90s)
  -r1 RANDSTART, --randstart RANDSTART
                        sets the start value of the randomizer. Minimum distance from the previous gif in seconds
                        (default 20s)
  -r2 RANDEND, --randend RANDEND
                        sets the end value of the randomizer. Maximum distance from the previous gif in seconds
                        (default 80s)
```

## Known Issues

Resolved: Script fails if the directories has a dot in them. 

```
IsADirectoryError: [Errno 21] Is a directory: 'Folder.with.a.dot'
```

## Author

Rootifera

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details

## FAQ

Q: Why are you using ffmpeg directly instead of using ffmpeg's python module?  
A: This is easier. I didn't want to go through all that documentation.

Q: Is this the most efficient way of generating gif files from videos?  
A: No idea, probably not. 

Q: Your code is an absolute mess, what kind of developer are you?  
A: I'm not a developer. I'm a SysAdmin, this is the best I can do. Don't like it? Improve it.

Q: I can't make it work. Can you help?  
A: Sure, please create an issue and I'll try my best to help.
