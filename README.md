## Extract images from Scans

This script uses OpenCV to find and extract images from scans. To run, clone repo, and then build and run the Docker container.

For example, if your image is in a subfolder `images`:
```
docker build -t extract_imgs .
docker run --mount type=bind,source="$(pwd)",target=/data extract_imgs -f /data/images/file.jpg -o /data/images/extracted/
```
The extracted images will be in `images/extracted/extracted`.

The build step will take quite a bit of time, while OpenCV is being built.
