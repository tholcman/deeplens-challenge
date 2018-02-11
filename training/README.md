# Notes on training 

Checkouted https://github.com/apache/incubator-mxnet/ and use subfolder `./example/ssd/`

Put files from here to corresponding directories in ssd example

## prepare dataset 
- files have `md5(original_name).jpg` name
- images are resized to max 500px
- annotations created with https://github.com/tzutalin/labelImg
- validation images has twice checked annotations - to not miss anything

```
ds/
├── Annotations [238 entries exceeds filelimit, not opening dir]
├── Images [238 entries exceeds filelimit, not opening dir]
├── train.txt
├── trainval.txt
└── val.txt
```
Generating dataset
```
python3 tools/prepare_dataset.py --dataset th --set train --root ds/ --target ./data/train.lst
python3 tools/prepare_dataset.py --dataset th --set val --root ds/ --target ./data/val.lst
```

## training
by default it tries to use pretrained model `vgg16_reduced`, I don't know if it is good for `ssd_resnet50` so I have turned it off: line 222 `train/train_net.py`

Create EC2 instance from 
```
# activate mxnet_p36 and downgrade mxnet to mxnet-cu90==0.11.1b20171009
# or create custom virtualenv with proper version ^
# for custom virtual env see mxnet getting started installation instruction

# checkout https://github.com/apache/incubator-mxnet/
git clone https://github.com/apache/incubator-mxnet.git
cd incubator-mxnet/example/ssd

# upload locally generated train.rec and val.rec to data/ folder 

# start training
nohup python train.py --train-path data/train.rec --val-path data/val.rec --class-names barbell --num-class 1 --network resnet50 --end-epoch 9999  &
tail -f nohup.out
# watch progress and kill process when satisfied with probabilities

# deploy
python3 deploy.py --prefix model/ssd_resnet50_300 --network resnet50 --num-class 20

# Install intel deeplearning deployment toolkit & convert or convert on device
cd model/
python3 /opt/awscam/intel/deeplearning_deploymenttoolkit/deployment_tools/model_optimizer/mxnet_converter/mo_mxnet_converter.py \ 
--models-dir ./ --output-dir ./ \
--model-name deploy_ssd_resnet50_300 \
--img-width 224 --img-height 224 \
--img-channels 3 --precision FP16 
--mean-var-r 123 --mean-var-g 117  --mean-var-b 104
# don't forget last 3 params ... see below where they come from
# upload to s3 and create model in Deeplens console
```

## mean pixels
I was stuck for few days when demo.py provide good results but converted model didn't. After building custom demo on video I have found that `mean_pixels` value are not default. Put print to `dataset/iterator.py` and try demo.py to get exact values
```python
        # line 168
        print('Mean_pixels', mean_pixels)
        # !!!! 
```