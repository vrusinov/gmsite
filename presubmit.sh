#!/bin/bash

pytype .
docker run --rm -e "WORKSPACE=${PWD}" -e "ENABLE_OSS_RISK=true" -v "$PWD:/app" --user $UID:$GID shiftleft/sast-scan scan
