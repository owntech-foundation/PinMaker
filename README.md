# PinMaker

![PinMaker banner](Images/pinmaker_banner.png "banner")

## Setup

clone the project `git clone https:/github.com/owntech-foundation/PinMaker.git`

install the dependencies with `python3 -m pip install -r requirements.txt`

## Plot Spin

run `python3 main.py -p input/SPIN.json -l`

## Options

The following options are supported

### Required

`-p` or `--pins` folled by the pins.json file you want to plot.
You may add multiple pin files in a single command.

### Optionals

`-l` or `legend` enable the **legend**

`-s` or `--style` followed by the **style.json** file. 
By default the style.json file is read.

`-o` or `--output` followed by the name of the **output.json** file.
By default the output file is **pinout.json**
