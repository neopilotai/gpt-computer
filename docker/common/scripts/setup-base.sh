#!/bin/bash
set -e

echo "====================BASE PACKAGES START===================="

apt-get update && apt-get upgrade -y

# Install standard base utilities
apt-get install -y --no-install-recommends 
    sudo curl wget git cron openssh-server ffmpeg supervisor 
    nodejs npm tesseract-ocr tesseract-ocr-script-latn poppler-utils 
    locales tzdata 
    tk tcl

# Set locale to en_US.UTF-8
sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && 
    dpkg-reconfigure --frontend=noninteractive locales && 
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

# Cleanup
apt-get clean && rm -rf /var/lib/apt/lists/*

echo "====================BASE PACKAGES END===================="
