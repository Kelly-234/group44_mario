from .head import DiscreteHead, DuelingHead, DistributionHead, RainbowHead, QRDQNHead, \
    QuantileHead, FQFHead, RegressionHead, ReparameterizationHead, MultiHead, head_cls_map, \
    independent_normal_dist
from .encoder import ConvEncoder, FCEncoder, IMPALAConvEncoder
from .utils import create_model
