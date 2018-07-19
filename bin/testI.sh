#!/bin/bash -e

# Copyright (c) 2018 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
# and/or its affiliated entities, under various laws including copyright, international treaties, patent,
# and/or contract. Any use of the material herein must be in accordance with the terms of the License.
# All rights not expressly granted by the License are reserved.
# Unless required by applicable law or agreed to separately in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

echo "Assuming Internet works"
return

RESULT_FOO=`python -c 'import testInternet; print testInternet.connected_to_internet()'`
if [[ $RESULT_FOO = "True" ]]
then 
	echo "Internet OK"
else
	echo "Internet Not OK"
	exit 1
fi
echo "End of the script!"