#!/usr/bin/bash
steps:
  - name: Create dot env file
  - shell: bash
    run: |
      touch .env
      echo "ACCESS_KEY=${{ secrets.ACCESS_KEY }}" >> .env