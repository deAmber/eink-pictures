#!/bin/bash

INT_HEX=$(i2cget -y 1 0x08 0x01)
DEC_HEX=$(i2cget -y 1 0x08 0x02)

INT=$((INT_HEX))
DEC=$((DEC_HEX))

echo "VOLTAGE=${INT}.$(printf "%02d" "$DEC")"
