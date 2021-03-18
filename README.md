## Overview
A TensorFlow implementation of [DeepOnKHATT: An End-to-End Arabic Online Handwriting Recognition System]

## Environment Setup
```
pip install -r requirements.txt
```

## Data Preparation 
All handwriting samples have to be in the following format 
```
679.785826771654 70.0346456692913 0
679.785826771654 70.0346456692913 0
679.181102362205 68.4850393700787 0
678.727559055118 67.8047244094488 0
678.047244094488 67.7291338582677 0
................. ............... .
................. ............... .
................. ............... .
................. ............... .
676.573228346457 70.2236220472441 1
```
The first column is x coordinate, the second column is y coordinate and the third column is pen up indicator. \

All samples files should have label file (examples and jupyter notebook provided in features directory)

## Configuration

General configuration can be found in neural_network.ini file

## Training
To start training from scratch run the following command: \
```
python train.py
```
To load the pre-trained model and continue training run the following command: \



```
python train.py --config neural_network.ini --name model.ckpt-20
```


## Building Language Model
**1. Cloning and making the KENLM** \
`
git clone https://github.com/kpu/kenlm
` 
\
then build it 


```
cd kenlm
mkdir -p build
cd build
cmake ..
make -j 4
```



**2.  Providing the corpus** \
The file of the corpus should have one Arabic sentence per line. Then, You will encode the entire file using the script provided in the features directory (data_preparation.ipynb).
\
 **3. Creating arpa file** \
```
./bin/lmplz --text corpus.txt --arpa words.arpa --o 3
```
**4. Building language model binary** \
```
./build_binary -T -s words.arpa lm.binary
```
**5. Building the trie** \
`./generate_trie alphabet.txt lm.binary trie`

## Running a demo

In this demo, you can demonstrate the full end2end DeepOnKHATT system and you can write on canvas and DeepOnKHATT will recognize your handwriting in real-time. Demo will be run in Google's Colaboratory, a Jupyter notebook environment that runs entirely in the cloud, you don't need to download anything to your local machine. 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fakhralwajih/DeepOnKHATT/blob/main/DeepOnKHATT.ipynb)


## Pre-trained model and LM model 
You can download them from the following links: \
https://drive.google.com/uc?id=1Z_gzzWVjskv_1JqErGuz8ZVfCSNaC3VY  \
https://drive.google.com/uc?id=1MqhnAcXMwT_nq_z-01CRhWKLYJYZBa1A  \
https://drive.google.com/uc?id=1-YAltfi_4Klvu_-f72iSkHboM46-iH_t 
