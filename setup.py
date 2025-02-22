import os

import torch
from setuptools import find_packages, setup
from torch.utils.cpp_extension import (BuildExtension, CppExtension,
                                       CUDAExtension)

with open('README.md', 'r') as fh:
    long_description = fh.read()


def make_cuda_ext(name,
                  module,
                  sources,
                  sources_cuda=[],
                  extra_args=[],
                  extra_include_path=[]):

    define_macros = []
    extra_compile_args = {'cxx': [] + extra_args}

    if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
        define_macros += [('WITH_CUDA', None)]
        extension = CUDAExtension
        extra_compile_args['nvcc'] = extra_args + [
            '-D__CUDA_NO_HALF_OPERATORS__',
            '-D__CUDA_NO_HALF_CONVERSIONS__',
            '-D__CUDA_NO_HALF2_OPERATORS__',
        ]
        sources += sources_cuda
    else:
        print('Compiling {} without CUDA'.format(name))
        extension = CppExtension
        # raise EnvironmentError('CUDA is required to compile MMDetection!')

    return extension(
        name='{}.{}'.format(module, name),
        sources=[os.path.join(*module.split('.'), p) for p in sources],
        include_dirs=extra_include_path,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
    )


setup(
    name='BEVDepth',
    version='0.0.1',
    author='Megvii',
    author_email='liyinhao@megvii.com',
    description='Code for BEVDepth',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=None,
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[],
    ext_modules=[
        make_cuda_ext(
            name='voxel_pooling_train_ext',
            module='bevdepth.ops.voxel_pooling_train',
            sources=['src/voxel_pooling_train_forward.cpp'],
            sources_cuda=['src/voxel_pooling_train_forward_cuda.cu'],
        ),
        make_cuda_ext(
            name='voxel_pooling_inference_ext',
            module='bevdepth.ops.voxel_pooling_inference',
            sources=['src/voxel_pooling_inference_forward.cpp'],
            sources_cuda=['src/voxel_pooling_inference_forward_cuda.cu'],
        ),
    ],
    cmdclass={'build_ext': BuildExtension}, #说白了这里有个voxel_pooling的算子
)
