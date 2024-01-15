# MOCR

## Setup

> Warning: This project was developed using Python 3.11. It is recommended to use the same version.

> Note: The setup described below is for Windows. If you are using another OS, you will have to install the dependencies manually.

### Install ORC Engine

1) Run `installer.exe` found in `tools` folder.
2) Once installation finishes, copy `tools\mal.traineddata` to `C:\Program Files\Tesseract-OCR\tessdata`

### Install Python Dependencies

1) Open a terminal in the root folder of the project.
2) Run `pip install -r requirements.txt`

## Usage

### Load Data
1) Create a folder named `data` in the root folder of the project.
2) Place the PDFs you want to process in the `data` folder.

### Run OCR

1) Open a terminal in the project root folder.
2) Run `python main.py` and wait for the process to finish.
3) The output will be in the `output` folder.

## Configuration

All configuration files are located in the `res` folder. Take a look at `replacements.csv` to see how to add new replacements. Take a look at `config.json` to change find and replace function.
