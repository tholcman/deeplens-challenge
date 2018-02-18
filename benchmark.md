# Benchmark

My guess is that 10 will be best for project.
Done on Deeplens Camera on deployed converted model.

| Network           | Size    | Speed [FPS]| Comment                          |
| ----------------- |:--------| ----------:| -------------------------------- |
| ssd_resnet50      | 224x224 | 4.7        |                                  |
| ssd_resnet50      | 160x160 | 6.0        | Weird as size is half of ^       |
| ssd_resnet50      | 300x300 | 2.0        |                                  |
| ssd_vgg16_reduced | 300x300 | 1.7        | I was not able to create smaller |
| ssd_inceptionv3   | 224x224 | 5.7        | Is not converging ... for now    |
| ssd_inceptionv3   | 160x160 | 7.2        | Is not converging ... for now    |
