# Tencent is pleased to support the open source community by making ncnn available.
#
# Copyright (C) 2021 THL A29 Limited, a Tencent company. All rights reserved.
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import torch
import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

    def forward(self, x, y, z, w):
        x = x * 2 - 1
        y = y * 2 - 1
        z = z * 2 - 1
        w = w * 2 - 1
        x = F.log_softmax(x, 0)
        y = F.log_softmax(y, 1)
        z = F.log_softmax(z, 2)
        # w = F.log_softmax(w, -1) TODO
        return x, y, z, w

def test():
    net = Model()
    net.eval()

    torch.manual_seed(0)
    x = torch.rand(16)
    y = torch.rand(2, 16)
    z = torch.rand(3, 12, 16)
    w = torch.rand(5, 7, 9, 11)

    a = net(x, y, z, w)

    # export torchscript
    mod = torch.jit.trace(net, (x, y, z, w))
    mod.save("test_F_log_softmax.pt")

    # torchscript to pnnx
    import os
    os.system("../../src/pnnx test_F_log_softmax.pt inputshape=[16],[2,16],[3,12,16],[5,7,9,11]")

    # ncnn inference
    import test_F_log_softmax_ncnn
    b = test_F_log_softmax_ncnn.test_inference()

    for a0, b0 in zip(a, b):
        if not torch.allclose(a0, b0, 1e-4, 1e-4):
            return False
    return True

if __name__ == "__main__":
    if test():
        exit(0)
    else:
        exit(1)
