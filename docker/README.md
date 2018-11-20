
[![Docker Automated buil](https://img.shields.io/docker/automated/enriquegrodrigo/docker-sparkdev.svg)](https://hub.docker.com/r/rcabanas/inferpy/)
[![Docker Build Statu](https://img.shields.io/docker/build/enriquegrodrigo/docker-sparkdev.svg)](https://hub.docker.com/r/rcabanas/inferpy/)
# inferpy-sparkdev

This is a base base image with InferPy package installed in a Linux System. 

## Docker Hub

One can easily obtain the latest image using:
```
docker pull rcabanas/inferpy:latest
```

## Building 

For building the container from the image in this folder:



```
$ ./build
```


## Usage

To run the container:

```
$ ./run
```

Then, a linux shell is open

```

root@fbe7863cddb2:/home/root# python3
Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
[GCC 8.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import inferpy


```